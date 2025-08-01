from orcapod.data.kernels import TrackedKernelBase
from orcapod.protocols import data_protocols as dp
from orcapod.types import TypeSpec
from abc import abstractmethod
from typing import Any
from collections.abc import Collection


class Operator(TrackedKernelBase):
    """
    Base class for all operators.
    Operators are a special type of kernel that can be used to perform operations on streams.

    They are defined as a callable that takes a (possibly empty) collection of streams as the input
    and returns a new stream as output (note that output stream is always singular).
    """


class UnaryOperator(Operator):
    """
    Base class for all operators.
    """

    def check_unary_input(
        self,
        streams: Collection[dp.Stream],
    ) -> None:
        """
        Check that the inputs to the unary operator are valid.
        """
        if len(streams) != 1:
            raise ValueError("UnaryOperator requires exactly one input stream.")

    def validate_inputs(self, *streams: dp.Stream) -> None:
        self.check_unary_input(streams)
        stream = streams[0]
        return self.op_validate_inputs(stream)

    def forward(self, *streams: dp.Stream) -> dp.Stream:
        """
        Forward method for unary operators.
        It expects exactly one stream as input.
        """
        stream = streams[0]
        return self.op_forward(stream)

    def kernel_output_types(self, *streams: dp.Stream) -> tuple[TypeSpec, TypeSpec]:
        stream = streams[0]
        return self.op_output_types(stream)

    def kernel_identity_structure(
        self, streams: Collection[dp.Stream] | None = None
    ) -> Any:
        """
        Return a structure that represents the identity of this operator.
        This is used to ensure that the operator can be uniquely identified in the computational graph.
        """
        if streams is not None:
            stream = list(streams)[0]
            self.op_identity_structure(stream)
        return self.op_identity_structure()

    @abstractmethod
    def op_validate_inputs(self, stream: dp.Stream) -> None:
        """
        This method should be implemented by subclasses to validate the inputs to the operator.
        It takes two streams as input and raises an error if the inputs are not valid.
        """
        ...

    @abstractmethod
    def op_forward(self, stream: dp.Stream) -> dp.Stream:
        """
        This method should be implemented by subclasses to define the specific behavior of the binary operator.
        It takes two streams as input and returns a new stream as output.
        """
        ...

    @abstractmethod
    def op_output_types(self, stream: dp.Stream) -> tuple[TypeSpec, TypeSpec]:
        """
        This method should be implemented by subclasses to return the typespecs of the input and output streams.
        It takes two streams as input and returns a tuple of typespecs.
        """
        ...

    @abstractmethod
    def op_identity_structure(self, stream: dp.Stream | None = None) -> Any:
        """
        This method should be implemented by subclasses to return a structure that represents the identity of the operator.
        It takes two streams as input and returns a tuple containing the operator name and a set of streams.
        """
        ...


class BinaryOperator(Operator):
    """
    Base class for all operators.
    """

    def check_binary_inputs(
        self,
        streams: Collection[dp.Stream],
    ) -> None:
        """
        Check that the inputs to the binary operator are valid.
        This method is called before the forward method to ensure that the inputs are valid.
        """
        if len(streams) != 2:
            raise ValueError("BinaryOperator requires exactly two input streams.")

    def validate_inputs(self, *streams: dp.Stream) -> None:
        self.check_binary_inputs(streams)
        left_stream, right_stream = streams
        return self.op_validate_inputs(left_stream, right_stream)

    def forward(self, *streams: dp.Stream) -> dp.Stream:
        """
        Forward method for binary operators.
        It expects exactly two streams as input.
        """
        left_stream, right_stream = streams
        return self.op_forward(left_stream, right_stream)

    def kernel_output_types(self, *streams: dp.Stream) -> tuple[TypeSpec, TypeSpec]:
        left_stream, right_stream = streams
        return self.op_output_types(left_stream, right_stream)

    def kernel_identity_structure(
        self, streams: Collection[dp.Stream] | None = None
    ) -> Any:
        """
        Return a structure that represents the identity of this operator.
        This is used to ensure that the operator can be uniquely identified in the computational graph.
        """
        if streams is not None:
            left_stream, right_stream = streams
            self.op_identity_structure(left_stream, right_stream)
        return self.op_identity_structure()

    @abstractmethod
    def op_validate_inputs(
        self, left_stream: dp.Stream, right_stream: dp.Stream
    ) -> None:
        """
        This method should be implemented by subclasses to validate the inputs to the operator.
        It takes two streams as input and raises an error if the inputs are not valid.
        """
        ...

    @abstractmethod
    def op_forward(self, left_stream: dp.Stream, right_stream: dp.Stream) -> dp.Stream:
        """
        This method should be implemented by subclasses to define the specific behavior of the binary operator.
        It takes two streams as input and returns a new stream as output.
        """
        ...

    @abstractmethod
    def op_output_types(
        self, left_stream: dp.Stream, right_stream: dp.Stream
    ) -> tuple[TypeSpec, TypeSpec]:
        """
        This method should be implemented by subclasses to return the typespecs of the input and output streams.
        It takes two streams as input and returns a tuple of typespecs.
        """
        ...

    @abstractmethod
    def op_identity_structure(
        self,
        left_stream: dp.Stream | None = None,
        right_stream: dp.Stream | None = None,
    ) -> Any:
        """
        This method should be implemented by subclasses to return a structure that represents the identity of the operator.
        It takes two streams as input and returns a tuple containing the operator name and a set of streams.
        """
        ...


class NonZeroInputOperator(Operator):
    """
    Operators that work with at least one input stream.
    This is useful for operators that can take a variable number of (but at least one ) input streams,
    such as joins, unions, etc.
    """

    def verify_non_zero_input(
        self,
        streams: Collection[dp.Stream],
    ) -> None:
        """
        Check that the inputs to the variable inputs operator are valid.
        This method is called before the forward method to ensure that the inputs are valid.
        """
        if len(streams) == 0:
            raise ValueError(
                f"Operator {self.__class__.__name__} requires at least one input stream."
            )

    def validate_inputs(self, *streams: dp.Stream) -> None:
        self.verify_non_zero_input(streams)
        return self.op_validate_inputs(*streams)

    def forward(self, *streams: dp.Stream) -> dp.Stream:
        """
        Forward method for variable inputs operators.
        It expects at least one stream as input.
        """
        return self.op_forward(*streams)

    def kernel_output_types(self, *streams: dp.Stream) -> tuple[TypeSpec, TypeSpec]:
        return self.op_output_types(*streams)

    def kernel_identity_structure(
        self, streams: Collection[dp.Stream] | None = None
    ) -> Any:
        """
        Return a structure that represents the identity of this operator.
        This is used to ensure that the operator can be uniquely identified in the computational graph.
        """
        return self.op_identity_structure(streams)

    @abstractmethod
    def op_validate_inputs(self, *streams: dp.Stream) -> None:
        """
        This method should be implemented by subclasses to validate the inputs to the operator.
        It takes two streams as input and raises an error if the inputs are not valid.
        """
        ...

    @abstractmethod
    def op_forward(self, *streams: dp.Stream) -> dp.Stream:
        """
        This method should be implemented by subclasses to define the specific behavior of the non-zero input operator.
        It takes variable number of streams as input and returns a new stream as output.
        """
        ...

    @abstractmethod
    def op_output_types(self, *streams: dp.Stream) -> tuple[TypeSpec, TypeSpec]:
        """
        This method should be implemented by subclasses to return the typespecs of the input and output streams.
        It takes at least one stream as input and returns a tuple of typespecs.
        """
        ...

    @abstractmethod
    def op_identity_structure(
        self, streams: Collection[dp.Stream] | None = None
    ) -> Any:
        """
        This method should be implemented by subclasses to return a structure that represents the identity of the operator.
        It takes zero or more streams as input and returns a tuple containing the operator name and a set of streams.
        If zero, it should return identity of the operator itself.
        If one or more, it should return a identity structure approrpiate for the operator invoked on the given streams.
        """
        ...
