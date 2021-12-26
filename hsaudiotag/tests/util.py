# Created By: Virgil Dupras
# Created On: 2009-05-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op

def eq_(a, b, msg=None):
    assert a == b, msg or "%r != %r" % (a, b)

class TestData:
    @staticmethod
    def filepath(relative_path, *args):
        if args:
            relative_path = op.join([relative_path] + list(args))
        datadirpath = op.join(op.dirname(__file__), 'testdata')
        resultpath = op.join(datadirpath, relative_path)
        assert op.exists(resultpath)
        return resultpath
