# coding = utf-8
"""responsible chain design pattern"""


class Request:
    """define your own request object"""
    pass


class Processor:
    """
    processor base class
    each processor can be connected to a successor (if necessary)
    when processor is not responsible to request
        call its successor to handle it
    """

    def __init__(self):
        self.__successor = None

    @property
    def successor(self):
        return self.__successor

    @successor.setter
    def successor(self, processor):
        assert isinstance(processor, Processor)
        self.__successor = processor

    def _check_request(self, request):
        """check if responsible to the given request"""
        raise NotImplementedError

    def _handle_request(self, request):
        """handle the given request"""
        raise NotImplementedError

    def handle_request(self, request):
        """external method to handle request"""
        assert isinstance(request, Request)
        if self._check_request(request):
            return self._handle_request(request)
        elif self.successor is not None:
            return self.successor.handle_request(request)


class ProcessorChain:
    """
    processor chain provide a list
        to manage relationship between processors
    processor chain is an optional object
        use processors only can be more flexible
    """

    def __init__(self):
        self.__processors = []

    def add(self, processor):
        """add processor to chain"""
        assert isinstance(processor, Processor)
        if self.__processors:
            self.__processors[-1].successor = processor
        self.__processors.append(processor)

    def handle_request(self, request):
        """handle request by chain"""
        if self.__processors:
            return self.__processors[0].handle_request(request)


# here follows a detail example


class MyRequest(Request):
    """
    initial my request with status
    status steps: SUBMITTED -> PENDING -> APPROVED
    """

    def __init__(self):
        self.status = None


class PendingProcessor(Processor):
    """processor to update 'SUBMITTED' requests to 'PENDING'"""

    def _check_request(self, request):
        return request.status == 'SUBMITTED'

    def _handle_request(self, request):
        request.status = 'PENDING'
        return True


class ApprovedProcessor(Processor):
    """processor to update 'PENDING' requests to 'APPROVED'"""

    def _check_request(self, request):
        return request.status == 'PENDING'

    def _handle_request(self, request):
        request.status = 'APPROVED'
        return True


if __name__ == '__main__':
    # make a 'SUBMITTED' request
    my_request = MyRequest()
    my_request.status = 'SUBMITTED'

    # build a processor chain
    chain = ProcessorChain()
    chain.add(PendingProcessor())
    chain.add(ApprovedProcessor())

    # update request status to 'PENDING'
    chain.handle_request(my_request)
    print(my_request.status)

    # update request status to 'APPROVED'
    chain.handle_request(my_request)
    print(my_request.status)
