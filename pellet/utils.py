from uuid import UUID


def is_uuid(string: str) -> bool:
    """
    Given a string, returns if it is a valid UUID
    :param string: String to check if is a valid UUID
    :return: True if string is a valid UUID else False
    """
    try:
        UUID(string)
        return True
    except ValueError:
        return False


def get_sanitised_path(path: str) -> str:
    """
    Given a path, returns it with all the path params(integers or UUIDs) replaced with "_id_"
    :param path: String which represents a path sent to Django; it is expected to be request.path
    :return: Path string with all path params(integers or UUIDs) replaced with "_id_"
    """
    # Adding a trailing slash if it doesn't exist
    if path == "" or path[-1] != "/":
        path += "/"

    return "/".join(
        [
            "_id_" if segment.isnumeric() or is_uuid(segment) else segment
            for segment in path.split("/")
        ]
    )
