"""Device models the API reports must not fall through to UNKNOWN."""

from __future__ import annotations

import pytest

from aiowithings import Device, DeviceModel, DeviceType


def _device(model_id: int, model: str) -> dict[str, object]:
    """Shape a getdevice entry, keeping only what Device.from_api reads."""
    return {
        "type": "Blood Pressure Monitor",
        "battery": "high",
        "model": model,
        "model_id": model_id,
        "first_session_date": None,
        "last_session_date": None,
        "deviceid": "d",
        "hash_deviceid": "d",
    }


@pytest.mark.parametrize(
    ("model_id", "raw_model", "device_type", "expected"),
    [
        (48, "BPM Vision", DeviceType.BLOOD_PRESSURE_MONITOR, DeviceModel.BPM_VISION),
        (71, "BeamO", DeviceType.SMART_CONNECTED_THERMOMETER, DeviceModel.BEAMO),
    ],
)
def test_model_is_recognised(
    model_id: int,
    raw_model: str,
    device_type: DeviceType,
    expected: DeviceModel,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Parse the model and device type documented by the Withings API."""
    device = Device.from_api({**_device(model_id, raw_model), "type": device_type})

    assert device.model is expected
    assert device.raw_model == raw_model
    assert device.device_type is device_type
    assert "unsupported value" not in caplog.text


def test_the_fluid_analyzer_device_type_is_recognised(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The U-Scan reports a type the enum did not carry; seen on a live account."""
    device = Device.from_api(
        {**_device(102, "WPA02"), "type": "Fluid Analyzer"},
    )

    assert device.device_type is DeviceType.FLUID_ANALYZER
    assert "unsupported value for <enum 'DeviceType'>" not in caplog.text


def test_an_unknown_device_type_still_falls_back(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The fallback has to survive, or this trades one gap for another."""
    device = Device.from_api({**_device(1, "WBS01"), "type": "Teleporter"})

    assert device.device_type is DeviceType.UNKNOWN
    assert "unsupported value" in caplog.text


def test_an_actually_unknown_model_still_falls_back(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The fallback has to keep working, or this trades one gap for another."""
    device = Device.from_api(_device(696969, "Futuristic device A"))

    assert device.model is DeviceModel.UNKNOWN
    assert "unsupported value" in caplog.text
