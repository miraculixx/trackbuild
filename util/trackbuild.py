class TrackBuildArgs(dict):
    def __init__(self, initial):
        for k,v in initial.iteritems():
            setattr(self, k, v)
        
    def __getattr__(self, key):
        try:
            return super(TrackBuildArgs, self).__getitem__(key)
        except KeyError:
            return None
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__    
