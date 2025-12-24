"""Module contains common test templates, to ease reusability of test code.

Naming conventions

Test Functions:
Examples, to get the idea:
- test_{function_name}_should_return_a_dict
- test_{function_name}_should_raise_when_empty_input_given
- test_{function_name}_should_drop_columns
- test_{function_name}_should_not_mutate_input

Test Groups:
Group tests when you see many that have something in common, such as the same class or same method under test.
**The intent is easier navigation and test filtering.**
Examples, to give ideas:
- Test{ClassName}
- Test{MethodName}
- Test{FunctionName}
- Test{FunctionName}{ErrorHandling}
"""

# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# sourcery skip: no-conditionals-in-tests

import contextlib
import re
import shutil
import sys
import time
import uuid
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import TYPE_CHECKING, Protocol
from unittest import mock

import pandas as pd  # type: ignore MissingImports
import pytest
from pyspark import sql  # type: ignore MissingImports
from pyspark.errors.exceptions import base  # type: ignore MissingImports
from pyspark.testing import utils  # type: ignore MissingImports

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Generator,
        Iterable,
        Iterator,
        MutableSequence,
        Sequence,
    )


def function_under_test(sequence_of_numbers: Sequence[int]) -> int:
    """Return the greatest number in a sequence."""
    if non_numbers_in_sequence := {
        maybe_number
        for maybe_number in sequence_of_numbers
        if not isinstance(maybe_number, int)  # type: ignore[UnnecessaryIsInstance]
    }:
        msg: str = f"Expected numbers in sequence, but found non-number: {non_numbers_in_sequence}"
        raise TypeError(msg)
    return max(sequence_of_numbers)


def test_standard_test_should_have_clear_setup_and_action_and_single_assert():
    # Given
    input_data = [1, 2, 3, 4, 5]

    # When
    actual = function_under_test(input_data)

    # Then
    expected = 5
    assert actual == expected


def test_function_name_should_do_expected_behavior():
    test_sequence = [1, 2, 3, 4, 5]

    actual = function_under_test(test_sequence)

    expected = 5
    assert actual == expected


def test_dataframes_should_equal():
    actual: pd.DataFrame = pd.DataFrame(
        [
            {"letter_column": "A", "number_column": 1},
            {"letter_column": "B", "number_column": 2},
            {"letter_column": "C", "number_column": 3},
        ]
    )
    expected: pd.DataFrame = pd.DataFrame(
        [
            {"letter_column": "C", "number_column": 3},
            {"letter_column": "A", "number_column": 1},
            {"letter_column": "B", "number_column": 2},
        ]
    )

    # Improved test output and can handle sorting situations
    with contextlib.suppress(base.PySparkAssertionError):
        """here are three different approaches to testing dataframes"""
        utils.assertDataFrameEqual(
            actual, expected, checkRowOrder=True
        )  # Most precise/strict
        utils.assertDataFrameEqual(actual, expected)  # default skips row order
        utils.assertDataFrameEqual(
            actual, expected, ignoreColumnName=False, ignoreColumnOrder=True
        )  # can be less precise

    # Risky; Avoid this seemingl intuitive approach.
    # It may work for trivial data on a single node local test runs, but is not deterministic.
    # assert actual.sort("number_column").collect() == expected.sort("number_column").collect()  # noqa: ERA001


class ClassUnderTest:
    def __init__(self, numbers_sequence: Sequence[int]) -> None:
        self._construction_guard_clause(numbers_sequence)

        self._numbers_sequence = numbers_sequence

    @staticmethod
    def _construction_guard_clause(numbers_sequence: Sequence[int]) -> None:
        if non_numbers_in_sequence := {
            maybe_number
            for maybe_number in numbers_sequence
            if not isinstance(maybe_number, int)  # type: ignore[reportUnnecessaryIsInstance]
        }:
            msg: str = f"Expected numbers in sequence, but found non-number: {non_numbers_in_sequence}"
            raise TypeError(msg)

    def method_under_test(self) -> int:
        return max(self._numbers_sequence)


class TestDoesNotRaise:
    def test_constructor_should_not_raise(self):
        """Great test to start with, to both cover when the constructor changes, and to demonstrate to readers how to create the object and its dependencies."""
        numbers_sequence: list[int] = [1, 2, 3, 4, 5]

        with does_not_raise():
            ClassUnderTest(numbers_sequence)

    def test_function_should_not_raise_with_valid_input(self):
        """May be required when working with untestable legacy codebases, or those with side-effects that are hard to isolate.

        It focuses on inputs instead of the direct behavior, but can be better than no tests at all.
        """
        test_sequence = [1, 2, 3, 4, 5]

        with does_not_raise():
            function_under_test(test_sequence)


class TestExceptionHandling:
    @staticmethod
    def function_with_exception_handling(sequence_of_numbers: list[int]) -> int:
        """Return the greatest number in a sequence."""
        if non_numbers_in_sequence := {
            maybe_number
            for maybe_number in sequence_of_numbers
            if not isinstance(maybe_number, int)  # type: ignore[reportUnnecessaryIsInstance]
        }:
            msg: str = f"Expected numbers in sequence, but found non-number: {non_numbers_in_sequence}"
            raise TypeError(msg)
        return max(sequence_of_numbers)

    def test_function_should_raise_type_error_when_non_number_given(self):
        """Simple example of catching an expected exception.

        Catching exceptions in order to give more context to the user should be a sensible default to strive for.
        """
        test_sequence = [1, "non_number"]

        expected_error_type: type[Exception] = TypeError
        with pytest.raises(expected_error_type):
            self.function_with_exception_handling(test_sequence)  # type: ignore[reportArgumentType]

    def test_function_should_raise_specific_msg_when_non_number_given(self):
        """Simple example of catching an expected exception.

        Catching exceptions in order to give more context to the user should be a sensible default to strive for.
        """
        test_sequence = [1, "non_number"]

        expected_error_type: type[Exception] = TypeError
        expected_error_message = r"Expected numbers in sequence, but found non-number: {'non_number'}"  # raw strings for regex, to avoid escaping characters
        with pytest.raises(expected_error_type, match=expected_error_message):
            self.function_with_exception_handling(test_sequence)  # type: ignore[reportArgumentType]

    def test_function_should_raise_general_msg_when_non_number_given(self):
        """Simple example of catching an expected exception.

        Catching exceptions in order to give more context to the user should be a sensible default to strive for.
        """
        test_sequence = [1, "non_number"]

        expected_error_type = TypeError
        expected_error_message = r"Expected numbers in sequence.* found non-number.*"  # raw strings for regex, to avoid escaping characters
        with pytest.raises(expected_error_type, match=expected_error_message):
            self.function_with_exception_handling(test_sequence)  # type: ignore[reportArgumentType]


class TestXfail:
    @staticmethod
    def function_with_unresolved_bug(_sequence_of_numbers: list[int]) -> int:
        """Dewonstrate a bug that is not yet fixed."""
        msg: str = "This function has a bug that is not yet resolved."
        raise ValueError(msg)

    @pytest.mark.xfail(
        reason="Unresolved bug, caused by... See issue JIRA-0000 for more details."
    )
    def test_function_should_raise_while_bug_unresolved(self):
        """Xfail should not be used without including a `reason`.

        Simple example of catching an expected exception in the test, marking it with an xfail to not halt ongoing development, and to communicate known details about the bug for the rest of the team.
        """
        input_data = [1, 2, 3, 4, 5]

        self.function_with_unresolved_bug(input_data)

    @pytest.mark.xfail(
        reason="Unresolved bug, caused by... Card JIRA-0000 has more details.",
        raises=ValueError,
    )
    def test_function_should_raise_specific_error_while_bug_unresolved(self):
        """Include specific error type, to aid the bughunt and inform the team.

        Sometimes a flaky part of a system fails for many reasons (commonly a Large Class with too many responsibilities).  It is helpful to have each bug captured in a test, and including each Error type raised helps to isolate each independent bughunt.
        This also helps reduce false-negatives when an undiscovered bug appears, and to detect when a bug unexpectedly gets fixed by a change.
        """
        input_data = [1, 2, 3, 4, 5]

        self.function_with_unresolved_bug(input_data)

    @staticmethod
    def function_that_is_not_implemented(_sequence_of_numbers: list[int]) -> int:
        """Demonstrate a feature that is not yet implemented."""
        msg: str = "This function is not yet implemented."
        raise NotImplementedError(msg)

    @pytest.mark.xfail(
        reason="Feature not yet implemented, Card JIRA-0000 has more details.",
        raises=NotImplementedError,
    )
    def test_function_should_raise_specific_error_when_not_implemented(self):
        """Technique for creating a test for a feature that is planned to be implemented later."""
        input_data = [1, 2, 3, 4, 5]

        self.function_that_is_not_implemented(input_data)

    @pytest.mark.xfail(
        condition=(sys.platform in ["darwin", "win32", "win64"]),
        reason="Platform-specific bug...",
    )
    def test_catch_platform_specific_bug_via_xfail_args(self):
        """There are times when a bug is caused by or expressed on a specific platform."""

        def _function_to_simulate_platform_based_error() -> None:
            if _is_problem_platform := sys.platform in ["darwin", "win32", "win64"]:
                msg: str = "Platform-specific bug"
                raise RuntimeError(msg)

        _function_to_simulate_platform_based_error()

    def test_catch_very_specific_bug_via_error_message(self):
        """Advanced technique may be necessary when a test is only partially failing, such as for a platform-specific bug, or a bug that only occurs in certain conditions.

        Inserting the xfail into a try-except block allows us to only apply an xfail when the bug is expressed.
        Note: If this is required more than once, a helper function for setup is advised to maintain test readability.
        """
        input_data = [1, 2, 3, 4, 5]

        expected_unresolved_bug_error_type: type[Exception] = ValueError
        expected_unresolved_bug_error_message = (
            r"This function has a bug that is not yet resolved."
        )
        xfail_bug_reason = "Unresolved bug, caused by... Card JIRA-0000 has more details."
        try:
            self.function_with_unresolved_bug(input_data)
        except expected_unresolved_bug_error_type as e:
            if _is_confirmed_bug := re.search(
                expected_unresolved_bug_error_message, str(e)
            ):
                pytest.xfail(reason=xfail_bug_reason)
            else:
                raise


class TestSkip:
    @pytest.mark.skipif(
        sys.version_info < (3, 10), reason="Requires Python 3.8 or higher"
    )
    def test_that_should_not_run_based_on_py_version(self):
        """Example of skipping a test based on the Python version."""

    @pytest.mark.skipif(
        sys.platform in ["darwin", "win32", "win64"],
        reason="Should not even be run on these platforms",
    )
    def test_that_should_not_run_based_on_platform(self):
        """In case some code is mistakenly coupled to a platform and should not executed."""

    @pytest.mark.skip(
        reason="Unresolved bug that is so bad, we should not even run this test"
    )
    def test_that_is_ruined_and_hard_to_catch_with_conditional(self):
        """Very rare case.  We may never need to do this, but it is possible.

        It should not be the first choice or a habit, else it's effectively like deleting the test instead of fixing a problem.
        """


class Transformer(Protocol):
    """Protocol, sometimes known as an Interface in other languages.

    It defines a set of expected attributes or methods that an object has.
    It enables type checking static analysis, Generic Programming and Polymorphism,
    but does not enforce the implementation.
    """

    def transform(self, input_data: sql.DataFrame) -> sql.DataFrame: ...


class FakeTransformer(Transformer):
    """a Fake, which is a type of Test Double.

    It is a simplified implementation for testing the Composite CLass.
    It enables faster test runtimes by avoiding expensive IO and compute.
    And enables one to develop a system in gradual parts, instead of all at once.
    """

    def transform(self, input_data: sql.DataFrame) -> sql.DataFrame:
        """Filter rows where the number_column is greater than 2."""
        return input_data.filter(input_data.number_column <= 2)


class TestFakeTransformer:
    def test_stub_transformer_should_filter_rows_greater_than_2(
        self, spark: sql.SparkSession
    ):
        """It is important to recognize testing with a stub is not testing the actual behavior of the system.

        So don't forget to test the non-Stub version as well.
        Creating a test suite for Test Doubles can ensure they best represent the real objects,
        and to avoid breaking changes to their behaviors.
        """
        stub_transformer: Transformer = FakeTransformer()
        input_data: sql.DataFrame = spark.createDataFrame(
            [
                sql.Row(letter_column="A", number_column=1),
                sql.Row(letter_column="B", number_column=2),
                sql.Row(letter_column="C", number_column=3),
            ]
        )

        actual: sql.DataFrame = stub_transformer.transform(input_data)
        expected = spark.createDataFrame(
            [
                sql.Row(letter_column="A", number_column=1),
                sql.Row(letter_column="B", number_column=2),
            ]
        )
        utils.assertDataFrameEqual(actual, expected)  # type: ignore[reportUnknownMemberType]


class CompositeClassUnderTest:
    """Class that will be used in our templates, to give a concrete example.

    It also demonstrates a basic use of Composition, where the behavior is provided by the Transformer object and passed in during construction.
    """

    def __init__(self, behavior_object: Transformer) -> None:
        self._behavior_object: Transformer = behavior_object

    def run(self, input_data: sql.DataFrame) -> sql.DataFrame:
        return self._transform(input_data)

    def _transform(self, input_data: sql.DataFrame) -> sql.DataFrame:
        return self._behavior_object.transform(input_data)


class TestCompositeClassUnderTest:
    def test_constructor_should_not_raise(self):
        """Great test to start with, to both cover when the constructor changes, and to demonstrate to readers how to create the object and its dependencies."""
        fake_transformer: Transformer = FakeTransformer()

        with does_not_raise():
            CompositeClassUnderTest(fake_transformer)

    def test_run_completes_full_behavior(self, spark: sql.SparkSession):
        """Straight-forward test design when a Composite Object handles a cohesive set of transformations.

        Often, Fakes can fill in when code is coupled to infrastructure details such as cloud services or datastores.
        """
        fake_transformer: Transformer = FakeTransformer()
        composite_object: CompositeClassUnderTest = CompositeClassUnderTest(
            fake_transformer
        )
        input_data: sql.DataFrame = spark.createDataFrame(
            [
                sql.Row(letter_column="A", number_column=1),
                sql.Row(letter_column="B", number_column=2),
                sql.Row(letter_column="C", number_column=3),
            ]
        )

        actual: sql.DataFrame = composite_object.run(input_data)
        expected = spark.createDataFrame(
            [
                sql.Row(letter_column="A", number_column=1),
                sql.Row(letter_column="B", number_column=2),
            ]
        )
        utils.assertDataFrameEqual(actual, expected)  # type: ignore[reportUnknownMemberType]

    def test_composite_object_calls_behavior_objects(self):
        """Test approach that may be helpful when a Fake or Stub is not easy to create yet.

        A common example is for untestable legacy codebases, when behavior is coupled directly to cloud services or infrastructure details.
        It can be useful to begin with this Spy-based test design to ensure forward progress.
        """
        spy_transformer: Transformer = mock.MagicMock(spec=FakeTransformer)
        composite_object: CompositeClassUnderTest = CompositeClassUnderTest(
            spy_transformer
        )
        dummy_data: sql.DataFrame = mock.MagicMock(spec=sql.DataFrame)

        composite_object.run(dummy_data)

        expected_method_call: mock.MagicMock = spy_transformer.transform
        expected_method_call.assert_called_once_with(dummy_data)


class AbstractRepository(Protocol):
    """Protocol, sometimes known as an Interface in other languages.

    It is often an important object to define during TDD, as it enables Test Doubles to accurately match the real objects
    while also being interchangeable (aka Plugin Architecture, Polymorphism).
    """

    def create(self, key: str, value: str) -> None: ...

    def read(self, key: str) -> str: ...


class CloudRepository(AbstractRepository):
    """Concrete implementation of the AbstractRepository.

    One to specifically illustrate why creating Test Doubles is important
    for maintaining a fast test suite.
    """

    def __init__(self) -> None:
        self._data_store: dict[str, str] = {}

    def _cloud_operation(self) -> None:
        """Illustrate the time loss of waiting for infrastructure operations."""
        time.sleep(10)

    def create(self, key: str, value: str) -> None:
        self._cloud_operation()
        self._data_store[key] = value

    def read(self, key: str) -> str:
        self._cloud_operation()
        return self._data_store[key]


class TestDoubles:
    @pytest.fixture
    def dummy_repo(self) -> AbstractRepository:
        class DummyRepo(AbstractRepository):
            """A Dummy Test Double stands in for dependencies such as construction or function calls, but is not actually used in execution.

            Note: Needing to use a Dummy may be an indicator of multiple responsibilities or lack of cohesion in the object under test.
            """

            def create(self, key: str, value: str) -> None: ...

            def read(self, key: str) -> str: ...

        return DummyRepo()

    def test_with_dummy_for_dependency(self, dummy_repo: AbstractRepository):
        """Example of using a Dummy.

        Key behaviors: stand-in for dependencies that are not used in the test.
        """

        # Given
        def function_that_requires_a_dependency(
            input_data: int, _unused_repo: AbstractRepository
        ) -> int:
            return input_data + 2

        input_data = 1

        # When
        actual = function_that_requires_a_dependency(input_data, dummy_repo)
        expected = 3

        # Then
        assert actual == expected

    def test_with_dummy_for_multiple_responsibilities(
        self, dummy_repo: AbstractRepository
    ):
        """Example of using a Dummy when the object under test has multiple responsibilities.

        Key behaviors: allow us to isolate the test to one behavior at a time.
        """

        # Given
        def function_that_does_too_much(
            input_data: int, repo: AbstractRepository
        ) -> tuple[int, str]:
            """Demonstrate common example of multiple responsibilities in a single object.

            Notice that the two returns are not related, and could be separated into two different functions.
            Before refactoring, we can use a Dummy to isolate the test to one behavior at a time.
            """
            doubled = input_data * 2
            data_store_value = repo.read(str(input_data))

            return doubled, data_store_value

        input_data = 1

        # When
        actual, _ = function_that_does_too_much(input_data, dummy_repo)
        expected = 2

        # Then
        assert actual == expected

    @pytest.fixture
    def fake_repo(self) -> AbstractRepository:
        class FakeRepo(AbstractRepository):
            """Fakes can be useful for replacing behaviors that are coupled to infrastructure details, or that have significant compute requirements.

            They can also stand in for Singletons such as global config store objects.
            """

            def __init__(self) -> None:
                self._data: dict[str, str] = {}

            def create(self, key: str, value: str) -> None:
                """Note the lack of time used with the cloud operation.

                Important benefit of using Fakes - keeping tests very fast.
                """
                self._data[key] = value

            def read(self, key: str) -> str:
                """Note the lack of time used with the cloud operation.

                Important benefit of using Fakes - keeping tests very fast.
                """
                return self._data[key]

        return FakeRepo()

    def test_with_fake(self, fake_repo: AbstractRepository):
        """Example of using a Fake.

        Key behaviors: provide working implementations, but not suitable for production.
        """

        def get_and_parse_value(repo: AbstractRepository, key: str) -> int:
            """Read from infrastructure, apply simple transformation, return value.

            Function represents a common example of a behavior that is commonly coupled to infrastructure details.
            But because of using a common Protocol/Interface, we can easily swap out the real object for a Fake.
            """
            value = repo.read(key)
            return int(value)

        # Given
        input_key = "2"
        fake_repo.create(input_key, "2")

        # When
        actual = get_and_parse_value(fake_repo, input_key)
        expected = 2

        # Then
        assert actual == expected

    @pytest.fixture
    def stub_repo(self) -> AbstractRepository:
        class StubRepo(AbstractRepository):
            """Stubs can be useful for providing static data or responses.

            They can also be used to simulate edge cases or error conditions.
            """

            def create(self, key: str, value: str) -> None: ...

            def read(self, key: str) -> str:  # noqa: ARG002
                return "2"

        return StubRepo()

    def test_with_stub(self, stub_repo: AbstractRepository):
        """Stubs are good for providing static data, to focus on the behavior of the object under test.

        Providing static data such as dataframes and arrays is one example, to keep tests deterministic.
        """

        def read_parse_sum_data(repo: AbstractRepository, keys: Iterable[str]) -> int:
            values: Iterator[str] = (repo.read(key) for key in keys)
            numbers: Iterator[int] = (int(value) for value in values)
            return sum(numbers)

        # Given
        input_keys = ["1", "2", "3"]

        # When
        actual = read_parse_sum_data(stub_repo, input_keys)
        expected = 6

        # Then
        assert actual == expected

    @pytest.fixture
    def mock_repo(self) -> AbstractRepository:
        class MockRepo(AbstractRepository):
            """Mocks are effectively a type of Spy, when the behavior is also wanted to be replaced.

            You can think of Mocks like a hybrid Dummy-Spy or Stub-Spy, depending on the use case.
            Key behaviors: record calls to the object, for assertion of arguments or sequence of calls.
            """

            def __init__(self) -> None:
                self.create_call_count: int = 0
                self.create_call_args: MutableSequence[tuple[str, str]] = []
                self.read_call_count: int = 0
                self.read_call_args: MutableSequence[str] = []

            def create(self, key: str, value: str) -> None:
                self.create_call_count += 1
                self.create_call_args.append((key, value))

            def read(self, key: str) -> str:
                """Return a static datum like a Stub might, but also recording the call."""
                self.read_call_count += 1
                self.read_call_args.append(key)
                return "2"

        return MockRepo()

    def test_with_mock(self, mock_repo: AbstractRepository):
        """Mocks are useful for recording interactions with the object under test.

        This is common for Composite Objects, that orchestrate the interactions of many modular objects to achieve a Usecase.
        """

        def load_many_values_sum_and_create_new_entry(
            repo: AbstractRepository, keys: Iterable[str]
        ) -> None:
            values: Iterator[str] = (repo.read(key) for key in keys)
            numbers: Iterator[int] = (int(value) for value in values)
            total = sum(numbers)
            repo.create("total", str(total))

        # Given
        input_keys = ["1", "2", "3"]

        # When
        load_many_values_sum_and_create_new_entry(mock_repo, input_keys)

        # Then
        assert mock_repo.create_call_count == 1  # type: ignore[reportAttributeAccessError]


class TestFixtures:
    """Fixtures are a powerful tool for handling setup and teardown of infrastructure, data, or objects.

    Anytime you are working with side-effects, such as IO, network, or databases, you should consider using a Fixture.
    key benefits: decouple tests from infrastructure details and reduce test runtime, ensure tests don't leave side-effects.
    """

    class DirectorySorter:
        """A simple object to illustrate the use of Fixtures.

        Responsibilities: parse a directory, and sort the files in it.
        Note: this object is not coupled to the details of the directory, such as hard-coded paths.
        """

        def __init__(self, directory: Path) -> None:
            self._directory: Path = directory

        def get_sorted_filepaths(self) -> Sequence[Path]:
            filepaths: Iterator[Path] = self._directory.iterdir()
            sorted_filepaths: list[Path] = sorted(filepaths)
            return tuple(sorted_filepaths)

    def test_10_handle_full_setup_and_cleanup(self):
        """Is the worst-case scenario of needing to pollute the test with setup and cleanup code.

        There is a persistent risk of leaving side-effects when errors occur.
        """
        # Setup
        uuid_suffix: str = str(
            uuid.uuid4()
        )  # uuid to ensure unique folder name, to avoid conflicts with other parallel tests
        # create the folder inside of /tmp/, to help ensure clean up even in case of test failure
        directory_name: str = f"/tmp/test_folder_{uuid_suffix}"  # noqa: S108
        directory: Path = Path(directory_name)
        directory.mkdir()

        file_1: Path = directory / "file_1.txt"
        file_2: Path = directory / "file_2.txt"
        file_1.touch()
        file_2.touch()

        # Given
        directory_sorter = self.DirectorySorter(directory)

        # When
        try:
            actual = directory_sorter.get_sorted_filepaths()
        finally:
            shutil.rmtree(directory)
        expected = (file_1, file_2)

        # Then
        assert actual == expected

        # Cleanup

    def test_20_use_empty_tmp_path_fixture(self, tmp_path: Path):
        """If your object is not coupled to the details of the directory, such as hard-coded paths, then the `tmp_path` fixture can be a great option for testing."""
        file_1: Path = tmp_path / "file_1.txt"
        file_2: Path = tmp_path / "file_2.txt"
        file_1.touch()
        file_2.touch()
        # Given
        directory_sorter = self.DirectorySorter(tmp_path)

        # When
        actual = directory_sorter.get_sorted_filepaths()
        expected = (file_1, file_2)

        # Then
        assert actual == expected

    @pytest.fixture
    def temp_folder_with_files(self, tmp_path: Path) -> Path:
        """When we see many cohesive tests using the same setup steps, it can be a good usecase for a fixture."""
        file_1: Path = tmp_path / "file_1.txt"
        file_2: Path = tmp_path / "file_2.txt"
        file_1.touch()
        file_2.touch()
        return tmp_path

    def test_30_use_setup_fixture(self, temp_folder_with_files: Path):
        """Contrast this test with the one above.  We can improve readability and reliability by moving some setup steps into a fixture."""
        # Given
        directory_sorter = self.DirectorySorter(temp_folder_with_files)

        # When
        actual = directory_sorter.get_sorted_filepaths()
        expected = (
            temp_folder_with_files / "file_1.txt",
            temp_folder_with_files / "file_2.txt",
        )

        # Then
        assert actual == expected

    @pytest.fixture
    def create_temp_folder_with_files(
        self, tmp_path: Path
    ) -> Callable[[Iterable[str]], Path]:
        """Is a fixture factory.  Is is useful when you need to parameterize the fixture differently in each test."""

        def wrapped_func(file_names: Iterable[str]) -> Path:
            filepaths: Iterator[Path] = (tmp_path / file_name for file_name in file_names)
            [file.touch() for file in filepaths]
            return tmp_path

        return wrapped_func

    def test_40_use_fixture_factory(
        self, create_temp_folder_with_files: Callable[[Iterable[str]], Path]
    ):
        # Setup
        file_names = ["file_1.txt", "file_2.txt"]
        temp_folder = create_temp_folder_with_files(file_names)

        # Given
        directory_sorter = self.DirectorySorter(temp_folder)

        # When
        actual = directory_sorter.get_sorted_filepaths()
        expected = (temp_folder / "file_1.txt", temp_folder / "file_2.txt")

        # Then
        assert actual == expected

    @pytest.fixture
    def create_temp_infrastructure_and_handle_cleanup(
        self, tmp_path: Path
    ) -> Generator[Callable[[Iterable[str]], Path]]:
        """Is also a fixture factory, but with a manual cleanup step after the yield.

        Fixtures ensure any code after the yield is run after the test, even if the test fails.
        """
        created_folders: MutableSequence[Path] = []  # collector of side-effects

        def wrapped_func(file_names: Iterable[str]) -> Path:
            sub_folder: Path = tmp_path / "sub_folder"
            sub_folder.mkdir()
            created_folders.append(
                sub_folder
            )  # collect side-effects, for reference during cleanup

            filepaths: Iterator[Path] = (
                sub_folder / file_name for file_name in file_names
            )
            [file.touch() for file in filepaths]

            return sub_folder

        yield wrapped_func

        [shutil.rmtree(folder) for folder in created_folders]  # cleanup steps

    def test_50_use_fixture_factory_with_cleanup(
        self,
        create_temp_infrastructure_and_handle_cleanup: Callable[[Iterable[str]], Path],
    ):
        # Setup
        file_names = ["file_1.txt", "file_2.txt"]
        temp_folder = create_temp_infrastructure_and_handle_cleanup(file_names)

        # Given
        directory_sorter = self.DirectorySorter(temp_folder)

        # When
        filepaths = directory_sorter.get_sorted_filepaths()
        actual = {filepath.name for filepath in filepaths}
        expected = {"file_1.txt", "file_2.txt"}

        # Then
        assert actual == expected
