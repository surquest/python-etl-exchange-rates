import os
from enum import Enum


def get_subdirectories(path, skip_hidden=True):
    """Returns a list of subdirectories in a given path.

    :param path: The path to search for subdirectories.
    :type path: str
    :param skip_hidden: Whether to skip hidden directories.
    :type skip_hidden: bool
    :return: list of subdirectories
    :rtype: list
    """

    subdirectories = []

    for name in os.listdir(path):
        dir_path = os.path.join(path, name)
        if os.path.isdir(dir_path):
            folder = dir_path.split("/")[-1]
            if skip_hidden is True and folder.startswith("."):
                continue
            else:
                subdirectories.append(dir_path.split("/")[-1])

    return subdirectories


def create_enum_class(enum_list, name="EnumClass"):
    """Creates an Enum class from a list of strings.

    :param name: Name of the Enum class.
    :type name: str
    :param enum_list: The list of strings to create the Enum class from.
    :type enum_list: list
    :return: Enum class
    :rtype: Enum
    """

    return Enum(name, [(item, item) for item in enum_list])
