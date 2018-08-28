__version__     = "0.0.1"
__url__         = "http://gitlab.jpl.nasa.gov:8000/browser/trunk/HySDS/hysds"
__description__ = "ASF"

def getHandler():
    '''
    Get the handler from this package
    '''
    #Import inside the funtion, to prevent problems loading module
    import asf.asf_query
    return asf.asf_query.asf()
