
import logging

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


logger = logging.getLogger(__name__)
logger.info(f'Imported sequencebuilderversion: {__version__}')
