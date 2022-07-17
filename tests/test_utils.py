from uuid import uuid4

import pytest

from pellet.utils import get_sanitised_path, is_uuid


def test_is_uuid():
    assert is_uuid(str(uuid4())) == True

    assert is_uuid(str(123)) == False

    with pytest.raises(TypeError):
        is_uuid(None)


def test_get_sanitised_path():
    with pytest.raises(TypeError):
        assert get_sanitised_path(None)

    assert get_sanitised_path("") == "/"
    assert get_sanitised_path("/") == "/"
    assert get_sanitised_path("/v2") == "/v2/"
    assert get_sanitised_path("/v2/") == "/v2/"
    assert get_sanitised_path("/app/very/important/api") == "/app/very/important/api/"
    assert get_sanitised_path("/app/very/important/api/") == "/app/very/important/api/"
    assert (
        get_sanitised_path("/app/v2/very/important/api")
        == "/app/v2/very/important/api/"
    )
    assert (
        get_sanitised_path("/app/v2/very/important/api/")
        == "/app/v2/very/important/api/"
    )
    assert get_sanitised_path("/123") == "/_id_/"
    assert get_sanitised_path("/123/") == "/_id_/"
    assert get_sanitised_path("/6ab69721-816f-479d-b6d4-8423cd17cee8") == "/_id_/"
    assert get_sanitised_path("/6ab69721-816f-479d-b6d4-8423cd17cee8/") == "/_id_/"
    assert (
        get_sanitised_path("/app/v2/very/important/api/123")
        == "/app/v2/very/important/api/_id_/"
    )
    assert (
        get_sanitised_path("/app/v2/very/important/api/123/")
        == "/app/v2/very/important/api/_id_/"
    )
    assert (
        get_sanitised_path("/app/v2/very/important/123/api")
        == "/app/v2/very/important/_id_/api/"
    )
    assert (
        get_sanitised_path("/app/v2/very/important/123/api/")
        == "/app/v2/very/important/_id_/api/"
    )
    assert (
        get_sanitised_path(
            "/app/v2/very/important/api/6ab69721-816f-479d-b6d4-8423cd17cee8"
        )
        == "/app/v2/very/important/api/_id_/"
    )
    assert (
        get_sanitised_path(
            "/app/v2/very/important/api/6ab69721-816f-479d-b6d4-8423cd17cee8/"
        )
        == "/app/v2/very/important/api/_id_/"
    )
    assert (
        get_sanitised_path(
            "/app/v2/very/important/6ab69721-816f-479d-b6d4-8423cd17cee8/api"
        )
        == "/app/v2/very/important/_id_/api/"
    )
    assert (
        get_sanitised_path(
            "/app/v2/very/important/6ab69721-816f-479d-b6d4-8423cd17cee8/api/"
        )
        == "/app/v2/very/important/_id_/api/"
    )
    assert (
        get_sanitised_path(
            "/app/v2/very/important/123/api/6ab69721-816f-479d-b6d4-8423cd17cee8"
        )
        == "/app/v2/very/important/_id_/api/_id_/"
    )
    assert (
        get_sanitised_path(
            "/app/v2/very/important/123/api/6ab69721-816f-479d-b6d4-8423cd17cee8/"
        )
        == "/app/v2/very/important/_id_/api/_id_/"
    )
