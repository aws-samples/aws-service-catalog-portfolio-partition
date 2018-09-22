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

class ResourceNotSupportedError(Exception):

    def __init__(self, resource_type):
        super(ResourceNotSupportedError, self).__init__()
        self.message = 'Resource of type {} is not supported'.format(resource_type)


class MissingTrustRelationshipError(Exception):

    def __init__(self):
        super(MissingTrustRelationshipError, self).__init__()
        self.message = 'Trust Relationship are missing'


class TagNotExist(Exception):

    def __init__(self, key):
        super(TagNotExist, self).__init__()
        self.message = 'Tag {} does not exist'.format(key)


class EventParsingError(Exception):

    def __init__(self, key):
        super(EventParsingError, self).__init__()
        self.message = 'Failed to parse key {} from the event'.format(key)


class FailedToFindOrCreateResource(Exception):

    Message = 'Failed to find or create resource with {}: {}'

    def __init__(self, field, value):
        super(FailedToFindOrCreateResource, self).__init__()
        self.message = self.Message.format(field, value)


class InvalidConfiguration(Exception):

    Message = 'Resource Configuration missed resource types: {}'

    def __init__(self, resource_types):
        super(InvalidConfiguration, self).__init__()
        self.message = self.Message.format(resource_types)

