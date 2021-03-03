from configparser import ConfigParser
from pathlib import Path
import logging

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


import sequence_builder
from sequence_builder.telemetry import start_telemetry


CONFIG_PATH = (Path(Path(sequence_builder.__file__).parent) /
               'conf' / 'telemetry.ini')

telemetry_config = ConfigParser()
telemetry_config.read(CONFIG_PATH)

if telemetry_config['Telemetry'].getboolean('enabled'):
    start_telemetry()

logger = logging.getLogger(__name__)
logger.info(f'Imported sequence_builderversion: {__version__}')
