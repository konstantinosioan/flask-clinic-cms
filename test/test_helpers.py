import os

from io import BytesIO
from PIL import Image

from helpers import valid_password, valid_image, save_image


def make_image_bytes(width=10, height=10, format="PNG"):
    image = Image.new("RGB", (width, height))
    buffer = BytesIO()

    image.save(buffer, format=format)
    buffer.seek(0)

    return buffer


def test_password_is_none():
    assert not valid_password(None)


def test_password_is_empty():
    assert not valid_password("")


def test_password_too_short():
    assert not valid_password("Pass1!!")


def test_password_no_uppercase():
    assert not valid_password("pass11!!")


def test_password_no_digit():
    assert not valid_password("Password!")


def test_password_no_special():
    assert not valid_password("Password1")


def test_valid_password_min_size():
    assert valid_password("Pass11!!")


def test_valid_password():
    assert valid_password("Password1!")


def test_valid_image():
    buffer = make_image_bytes()
    assert valid_image(buffer)


def test_invalid_image():
    buffer = BytesIO(b"Hello, world")
    assert not valid_image(buffer)


def test_invalid_image_format():
    buffer = make_image_bytes(format="GIF")
    assert not valid_image(buffer)


def test_invalid_image_oversized():
    buffer = make_image_bytes(width=8000, height=8000)
    assert not valid_image(buffer)


def test_heic_is_valid():
    buffer = make_image_bytes(format="HEIF")
    assert valid_image(buffer)


def test_heic_saved_as_jpg():
    buffer = make_image_bytes(format="HEIF")
    filename = save_image(buffer)

    assert filename.endswith(".jpg")

    path = os.path.join("static", "uploads", filename)
    file = Image.open(path)

    try:
        assert file.format == "JPEG"
    finally:
        os.remove(path)


def test_exif_metadata_stripped():
    image = Image.new("RGB", (10, 10))
    exif = image.getexif()
    exif[271] = "test"
    buffer = BytesIO()
    image.save(buffer, format="JPEG", exif=exif)
    buffer.seek(0)

    filename = save_image(buffer)
    path = os.path.join("static", "uploads", filename)

    file = Image.open(path)

    try:
        assert len(file.getexif()) == 0
    finally:
        os.remove(path)
