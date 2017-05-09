#!/usr/bin/env python2
import pika


class SimpleQueueService():
    def __init__(self, app, logger):
        self.callbacks = {}
        self.configs = {}

        self.amqp_host = app.config.get('AMQP_HOST')
        self.amqp_host_fallback = app.config.get('AMQP_HOST_FALLBACK')

        self.logger = logger

    def _get_channel(self, fallback=True):
        try:
            amqp = pika.BlockingConnection(pika.ConnectionParameters(host=self.amqp_host))
            return amqp.channel()
        except:
            self.logger.error("AMQP CONNECTION FAILED")
            if fallback:
                self.logger.error("Attempting Fallback Connection")
            try:
                amqp = pika.BlockingConnection(pika.ConnectionParameters(host=self.amqp_host_fallback))
                return amqp.channel()
            except:
                self.logger.error("AMQP FALLBACK CONNECTION FAILED")

    def send(self, exchange, routing_key, body):
        channel = self._get_channel()
        try:
            channel.basic_publish(exchange, routing_key, body)
        except:
            self.logger.error("FAILED: " + body)
