"""Config flow for the Kef Connector integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from pykefcontrol.kef_connector import KefAsyncConnector
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_MAX_VOLUME,
    CONF_SPEAKER_MODEL,
    CONF_VOLUME_STEP,
    DEFAULT_MAX_VOLUME,
    DEFAULT_NAME,
    DEFAULT_SPEAKER_MODEL,
    DEFAULT_VOLUME_STEP,
    DOMAIN,
    FIRMWARE_MODELS,
    MODEL_LABELS,
    SOURCES,
)

_LOGGER = logging.getLogger(__name__)

CONNECTION_ERRORS = (aiohttp.ClientError, OSError, asyncio.TimeoutError)

MODEL_SELECTOR = SelectSelector(
    SelectSelectorConfig(
        options=[
            SelectOptionDict(value=model, label=label)
            for model, label in MODEL_LABELS.items()
        ],
        mode=SelectSelectorMode.DROPDOWN,
    )
)


class CannotConnect(Exception):
    """Error to indicate the speaker could not be reached."""


async def async_get_speaker_info(hass, host: str) -> dict[str, str | None]:
    """Query the speaker for its MAC address, name and model."""
    connector = KefAsyncConnector(host, session=async_get_clientsession(hass))
    try:
        async with asyncio.timeout(10):
            mac = await connector.mac_address
            name = await connector.speaker_name
            firmware_model = await connector.get_speaker_model()
    except CONNECTION_ERRORS as err:
        raise CannotConnect from err

    return {
        "mac": format_mac(mac),
        "name": name,
        "model": FIRMWARE_MODELS.get(firmware_model),
    }


def _options_schema(options: dict[str, Any]) -> vol.Schema:
    """Build the schema shared by the model step and the options flow."""
    return vol.Schema(
        {
            vol.Required(
                CONF_SPEAKER_MODEL,
                default=options.get(CONF_SPEAKER_MODEL, DEFAULT_SPEAKER_MODEL),
            ): MODEL_SELECTOR,
            vol.Required(
                CONF_MAX_VOLUME,
                default=options.get(CONF_MAX_VOLUME, DEFAULT_MAX_VOLUME),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=0, max=1, step=0.01, mode=NumberSelectorMode.SLIDER
                )
            ),
            vol.Required(
                CONF_VOLUME_STEP,
                default=options.get(CONF_VOLUME_STEP, DEFAULT_VOLUME_STEP),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=0.01, max=1, step=0.01, mode=NumberSelectorMode.BOX
                )
            ),
        }
    )


class KefConnectorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kef Connector."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._host: str | None = None
        self._info: dict[str, str | None] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler."""
        return KefConnectorOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the IP address of the speaker."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                info = await async_get_speaker_info(self.hass, host)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error while connecting to %s", host)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["mac"])
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                self._host = host
                self._info = info
                return await self.async_step_settings()

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema({vol.Required(CONF_HOST): str}), user_input
            ),
            errors=errors,
        )

    async def async_step_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Let the user confirm the detected model and volume settings."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._info["name"] or self._host,
                data={CONF_HOST: self._host},
                options=user_input,
            )

        return self.async_show_form(
            step_id="settings",
            data_schema=_options_schema(
                {CONF_SPEAKER_MODEL: self._info["model"] or DEFAULT_SPEAKER_MODEL}
            ),
            description_placeholders={
                "name": self._info["name"] or self._host,
                "host": self._host,
            },
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the IP address of an existing speaker."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                info = await async_get_speaker_info(self.hass, host)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error while connecting to %s", host)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["mac"])
                self._abort_if_unique_id_mismatch(reason="wrong_speaker")
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_HOST: host}
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema({vol.Required(CONF_HOST): str}),
                user_input or entry.data,
            ),
            errors=errors,
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> ConfigFlowResult:
        """Import a speaker configured in configuration.yaml."""
        host = import_data[CONF_HOST]
        try:
            info = await async_get_speaker_info(self.hass, host)
        except CannotConnect:
            return self.async_abort(reason="cannot_connect")
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Unexpected error while importing %s", host)
            return self.async_abort(reason="unknown")

        await self.async_set_unique_id(info["mac"])
        self._abort_if_unique_id_configured()

        speaker_model = import_data[CONF_SPEAKER_MODEL].upper()
        if speaker_model not in SOURCES:
            speaker_model = info["model"] or DEFAULT_SPEAKER_MODEL

        name = import_data[CONF_NAME]
        if name == DEFAULT_NAME:
            name = info["name"] or host

        return self.async_create_entry(
            title=name,
            data={CONF_HOST: host},
            options={
                CONF_SPEAKER_MODEL: speaker_model,
                CONF_MAX_VOLUME: import_data[CONF_MAX_VOLUME],
                CONF_VOLUME_STEP: import_data[CONF_VOLUME_STEP],
            },
        )


class KefConnectorOptionsFlow(OptionsFlow):
    """Handle options for Kef Connector."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the speaker options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(dict(self.config_entry.options)),
        )
