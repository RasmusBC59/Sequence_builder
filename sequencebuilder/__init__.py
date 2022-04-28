from configparser import ConfigParser
from pathlib import Path
import logging

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


import sequencebuilder

logger = logging.getLogger(__name__)
logger.info(f'Imported sequencebuilderversion: {__version__}')
