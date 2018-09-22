'''
 Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 Permission is hereby granted, free of charge, to any person obtaining a copy of this
 software and associated documentation files (the "Software"), to deal in the Software
 without restriction, including without limitation the rights to use, copy, modify,
 merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from helpers.logger import logger
from helpers.exceptions import ResourceNotSupportedError
RESOURCES_MOD_PATH = 'helpers.resources.{}'


class Factory(object):

    def __new__(
        cls,
        rtype,
        physical_id,
        resources_mod_path=RESOURCES_MOD_PATH,
        **kwargs
    ):
        rcls = rtype.replace('::', '')[3:]
        if 'Custom' in rtype:
            rcls = 'Custom'
            rtype = 'AWS::Custom'
        try:
            rmod = __import__(
                resources_mod_path.format(
                    rtype.replace('::', '_')[4:].lower()
                ),
                globals(),
                locals(),
                ['{}'.format(rcls)],
                0
            )
        except ImportError as e:
            if e.__class__ == 'ModuleNotFoundError':
                raise ResourceNotSupportedError(rtype)
            raise e
        instance = getattr(rmod, rcls)(physical_id, **kwargs)
        return instance
