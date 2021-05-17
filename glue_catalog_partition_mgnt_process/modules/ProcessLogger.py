import logging

def setup_logging():
    """
    Setup logging configuration
    """
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO,force=True)
    #logging.getLogger().setLevel(logging.INFO) on if using python 2.* or python 3.* (<3.8)
    
    return logging