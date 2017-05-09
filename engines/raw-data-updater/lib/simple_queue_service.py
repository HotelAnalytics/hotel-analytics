#!/usr/bin/env python2
import pika
import json
import traceback


class SimpleQueueService():
    def __init__(self, config, logger, prod=False):
        self.callbacks = {}
        self.configs = {}

        self.amqp_uri = config.AMQP_URI if not prod else config.AMQP_URI_PROD
        self.amqp_uri_fallback = config.AMQP_URI_FALLBACK if not prod else config.AMQP_URI_FALLBACK_PROD

        self.logger = logger
        self.receive_channel = self._get_channel(fallback=False)

    def _get_channel(self, fallback=True):
        try:
            amqp = pika.BlockingConnection(pika.URLParameters(self.amqp_uri))
            return amqp.channel()
        except:
            self.logger.error("AMQP CONNECTION FAILED")
            if fallback:
                self.logger.error("Attempting Fallback Connection")
            try:
                amqp = pika.BlockingConnection(pika.URLParameters(self.amqp_uri_fallback))
                return amqp.channel()
            except:
                self.logger.error("AMQP FALLBACK CONNECTION FAILED")

    def setup(self, config, callback, delay_exchange=False):
        queue_name = config['AMQP_QUEUE']
        error_queue_name = config['AMQP_QUEUE_ERROR']
        exchange_name = config['AMQP_EXCHANGE']

        default_routing_key = queue_name
        default_error_routing_key = error_queue_name

        self.configs[default_routing_key] = config

        if delay_exchange:
            self.receive_channel.exchange_declare(
                exchange=exchange_name,
                type='x-delayed-message',
                durable=True,
                arguments={
                    'x-delayed-type': 'topic'
                }
            )
        else:
            self.receive_channel.exchange_declare(exchange=exchange_name, type='topic', durable=True)

        self.receive_channel.queue_declare(queue=queue_name, durable=True)
        self.receive_channel.queue_declare(queue=error_queue_name, durable=True)

        # Set up exchange bindings to queues
        self.receive_channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=default_routing_key)
        self.receive_channel.queue_bind(exchange=exchange_name, queue=error_queue_name, routing_key=default_error_routing_key)

        if 'AMQP_QUEUE_ROUTING_KEY' in config:
            self.receive_channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=config['AMQP_QUEUE_ROUTING_KEY'])
            self.configs[config['AMQP_QUEUE_ROUTING_KEY']] = config
            self.callbacks[config['AMQP_QUEUE_ROUTING_KEY']] = callback
        if 'AMQP_QUEUE_ERROR_ROUTING_KEY' in config:
            self.receive_channel.queue_bind(exchange=exchange_name, queue=error_queue_name, routing_key=config['AMQP_QUEUE_ERROR_ROUTING_KEY'])

        self.callbacks[default_routing_key] = callback
        self.logger.info("Waiting for messages")
        self.receive_channel.basic_consume(self.process_request, queue=queue_name, no_ack=False)

    def process_request(self, ch, method, properties, body):
        callback = self.callbacks[method.routing_key]
        config = self.configs[method.routing_key]

        ch.basic_ack(delivery_tag=method.delivery_tag)
        try:
            if callback(body):
                self.logger.info("Processed")
            else:
                self.logger.error("Error Inserting Error Report")
                self.send(config['AMQP_EXCHANGE'], config['AMQP_QUEUE_ERROR'], body)
        except Exception as ex:
            self.logger.error(traceback.print_exc())
            self.logger.error(ex)
            self.send(config['AMQP_EXCHANGE'], config['AMQP_QUEUE_ERROR'], body)

    def send(self, exchange, routing_key, body):
        channel = self._get_channel()
        try:
            channel.basic_publish(exchange, routing_key, body)
        except:
            self.logger.error("FAILED: " + body)

    def get(self, queue, count=1):
        channel = self._get_channel()

        messages = []
        i = 0
        while True:
            if (count > 0 and i < count) or count == 0:
                try:
                    method_frame, header_frame, body = channel.basic_get(queue)

                    if method_frame:
                        print(method_frame)
                        print(header_frame)
                        print(body)

                        messages.append(method_frame)
                    else:
                        print('No messages to get')
                        break
                except:
                    self.logger.error('Failed to get messages from "{}" queue - {}'.format(queue, traceback.print_exc()))

                i += 1
            else:
                break

        for msg in messages:
            channel.basic_nack(msg.delivery_tag)

    def requeue_errors(self, error_queue, exchange, routing_key, count=1, ack=True, mutator=None):
        channel = self._get_channel()

        i = 0
        while True:
            if (count > 0 and i < count) or count == 0:
                try:
                    method_frame, header_frame, body = channel.basic_get(error_queue)

                    if method_frame:
                        body = json.loads(body)

                        if mutator is not None and hasattr(mutator, '__call__'):
                            body = mutator(body)

                        # Republish the message
                        channel.basic_publish(exchange, routing_key, json.dumps(body))

                        print('Requeued an error message: {}'.format(str(method_frame)))

                        if ack:
                            # Ack the error message so it is removed from the error queue
                            channel.basic_ack(method_frame.delivery_tag)
                    else:
                        break
                except:
                    self.logger.error('Failed to requeue error message from "{}" queue - {}'.format(error_queue, traceback.print_exc()))

                i += 1
            else:
                break

    def run(self):
        try:
            self.receive_channel.start_consuming()
        except KeyboardInterrupt:
            pass
