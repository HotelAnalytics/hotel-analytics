from os import getenv

APP_NAME = getenv('APP_NAME', 'episode-manager')
API_APP_NAME = getenv('API_APP_NAME', '{}-api'.format(APP_NAME))

CERTS_PATH = getenv('CERTS_PATH', '/sltc-certs/sltc-ca.crt')

ENGINE_ENV = getenv('ENGINE_ENV', 'dev')

SMPL_URI = getenv('SMPL_URI', 'mssql+pyodbc://datacompare:datacompar3@flowerpecker.simpleltc.local/SMPL?driver=FreeTDS&port=1433&odbc_options="TDS_Version=8"')
SQLALCHEMY_DATABASE_URI = SMPL_URI

ICD_URI = getenv('ICD_URI', 'postgresql://postgres:7Yq$J8eC@llama.simpleltc.local/icd')

LOG_ENABLED = bool(int(getenv('LOG_ENABLED', '1')))
LOG_LOCAL = bool(int(getenv('LOG_LOCAL', '1')))
LOG_REMOTE = bool(int(getenv('LOG_REMOTE', '0')))

SQLALCHEMY_RECORD_QUERIES = bool(int(getenv('RECORD_QUERIES', '0')))
LONG_QUERY_THRESHOLD = float(getenv('LONG_QUERY_THRESHOLD', 1.0))
SQLALCHEMY_TRACK_MODIFICATIONS = bool(int(getenv('SQLALCHEMY_TRACK_MODIFICATIONS', '0')))

DATAW_URI = getenv('DATAW_URI', 'mysql+mysqlconnector://mds_import:mds!mport@maria-dev.simpleltc.local/warehouse')

ES_USER = getenv('ES_USER', 'devuser')
ES_PASSWORD = getenv('ES_PASSWORD', 'Abc@123!')
ES_HOST = getenv('ES_HOST', 'elastic-dev2.simpleltc.local')
ES_PORT = getenv('ES_PORT', '443')
ES_USE_SSL = bool(int(getenv('ES_USE_SSL', '1')))

EPISODES_ALIAS = getenv('EPISODES_ALIAS', 'resident_episodes')
QUALITY_MEASURES_ALIAS = getenv('QUALITY_MEASURES_ALIAS', 'quality_measures')
PROVIDER_INFO_ALIAS = getenv('PROVIDER_INFO_ALIAS', 'provider_info')
DEFICIENCIES_ALIAS = getenv('DEFICIENCIES_ALIAS', 'deficiencies')
PENALTIES_ALIAS = getenv('PENATIES_ALIAS', 'penalties')

REINDEX_WORKER_THREADS = getenv('REINDEX_WORKER_THREADS', 4)
QM_CALC_REINDEX_WORKER_THREADS = getenv('QM_CALC_REINDEX_WORKER_THREADS', 4)
MEDICARE_API_WORKER_THREADS = getenv('MEDICARE_API_WORKER_THREADS', 4)

REHOSPITALIZATIONS_MODEL_FILE = getenv('REHOSPITALIZATIONS_MODEL_FILE', '/ml-models/2016-04-20-rehospitalization_model.dat')

MONGODB_URI = getenv('MONGODB_URI', 'mongodb://mongo-dev.simpleltc.local:27017')
# Nursing Home Compare (NHC)
MONGODB_NHC_ARCHIVES_DB = getenv('MONGODB_NHC_ARCHIVES_DB', 'nursing-home-compare-archives')
MONGODB_HISTORY_COLLECTION = getenv('MONGODB_HISTORY_COLLECTION', 'archive_history')
MONGODB_QM_COLLECTION = getenv('MONGODB_QM_COLLECTION', 'quality_measures')
MONGODB_CLAIM_QM_COLLECTION = getenv('MONGODB_QM_COLLECTION', 'claim_quality_measures')
MONGODB_PROVIDER_INFO_COLLECTION = getenv('MONGODB_PROVIDER_INFO_COLLECTION', 'provider_info')
MONGODB_DEFICIENCIES_COLLECTION = getenv('MONGODB_DEFICIENCIES_COLLECTION', 'deficiencies')
MONGODB_PENALTIES_COLLECTION = getenv('MONGODB_PENALTIES_COLLECTION', 'penalties')

AMQP_URI = getenv('AMQP_URI', 'amqp://dev_user:Abc123!@rabbit-dev.simpleltc.local')
AMQP_URI_FALLBACK = getenv('AMQP_URI_FALLBACK', 'amqp://dev_user:Abc123!@rabbit-dev.simpleltc.local')

AMQP_URI_PROD = getenv('AMQP_HOST_PROD', 'amqp://rabbit-ha.simpleltc.local')
AMQP_URI_FALLBACK_PROD = getenv('AMQP_HOST_FALLBACK_PROD', 'amqp://rabbit-ha.simpleltc.local')

MDS_AMQP_EXCHANGE = getenv('MDS_AMQP_EXCHANGE', 'sltc.mds')
MDS_WAREHOUSE_SYNC_ROUTING_KEY = getenv('MDS_WAREHOUSE_SYNC_ROUTING_KEY', 'assessment.warehouse.synced')
EPISODE_UPDATE_QUEUE = getenv('EPISODE_UPDATE_QUEUE', 'episode.update')
EPISODE_UPDATE_ERROR_QUEUE = getenv('EPISODE_UPDATE_ERROR_QUEUE', 'episode.update_error')

EPISODE_AMQP_EXCHANGE = getenv('EPISODE_AMQP_EXCHANGE', 'sltc.episode')
EPISODE_UPDATED_ROUTING_KEY = getenv('EPISODE_UPDATED_ROUTING_KEY', 'episode.updated')
QM_UPDATE_QUEUE = getenv('QM_UPDATE_QUEUE', 'qm.update')
QM_UPDATE_ERROR_QUEUE = getenv('QM_UPDATE_ERROR_QUEUE', 'qm.update_error')

# Five-star exchange and queues
MDS_5STAR_UPDATE_EXCHANGE = getenv('MDS_5STAR_UPDATE_EXCHANGE', 'sltc.mds.5star')
UPDATE_5STAR_REFERENCES_ROUTING_KEY = getenv('UPDATE_5STAR_REFERENCES_ROUTING_KEY', '5star.official.update_references')
UPDATE_5STAR_REFERENCES_QUEUE = getenv('UPDATE_5STAR_REFERENCES_QUEUE', '5star.official.update_references')
UPDATE_5STAR_REFERENCES_ERROR_QUEUE = getenv('UPDATE_5STAR_REFERENCES_ERROR_QUEUE', '5star.official_update_references_error')

# Episode recalculation exchange and queues
EPISODE_DELAY_EXCHANGE = getenv('EPISODE_DELAY_EXCHANGE', 'sltc.episode.delay')
EPISODE_RECALCULATION_QUEUE = getenv('EPISODE_RECALCULATION_QUEUE', 'episode.recalculate')
EPISODE_RECALCULATION_ERROR_QUEUE = getenv('EPISODE_RECALCULATION_ERROR_QUEUE', 'episode.recalculate_error')
EPISODE_RECALCULATION_ROUTING_KEY = getenv('EPISODE_RECALCULATION_ROUTING_KEY', 'episode.recalculate')

# QM recalculation queues
QM_DELAY_EXCHANGE = getenv('QM_DELAY_EXCHANGE', 'sltc.qm.delay')
QM_RECALCULATION_QUEUE = getenv('QM_RECALCULATION_QUEUE', 'qm.recalculate')
QM_RECALCULATION_ERROR_QUEUE = getenv('QM_RECALCULATION_ERROR_QUEUE', 'qm.recalculate_error')
QM_RECALCULATION_ROUTING_KEY = getenv('QM_RECALCULATION_ROUTING_KEY', 'qm.recalculate')

SOCRATA_APP_TOKEN = getenv('SOCRATA_APP_TOKEN', 'ZLrjRVxakNMrGRHO1VbrPhLRG')
API_PAGE_SIZE = getenv('API_PAGE_SIZE', 1000)

PROVIDER_INFO_URL = getenv('PROVIDER_INFO_URL', 'https://data.medicare.gov/resource/4pq5-n9py.json')
QUALITY_MEASURES_URL = getenv('QUALITY_MEASURES_URL', 'https://data.medicare.gov/resource/djen-97ju.json')
CLAIMS_MEASURES_URL = getenv('CLAIMS_MEASURES_URL', 'https://data.medicare.gov/resource/crzz-t9dk.json')
STATE_AVERAGES_URL = getenv('STATE_AVERAGES_URL', 'https://data.medicare.gov/resource/74hz-j434.json')
DEFICIENCIES_URL = getenv('DEFICIENCIES_URL', 'https://data.medicare.gov/resource/ikq5-jt9b.json')
PENALTIES_URL = getenv('PENALTIES_URL', 'https://data.medicare.gov/resource/im9k-ugyp.json')
