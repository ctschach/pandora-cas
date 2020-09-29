"""
TODO

DETAILS
"""
import logging
from typing import Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import CONN_CLASS_CLOUD_POLL
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL, MIN_POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)

FLOW_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str, vol.Optional(CONF_POLLING_INTERVAL,): int,}
)


def _base_schema(discovery_info=None):
    """Generate base schema."""
    base_schema = {}

    if discovery_info:
        base_schema.update(
            {
                vol.Required(CONF_USERNAME, description={"suggested_value": discovery_info[CONF_USERNAME]}): str,
                vol.Required(CONF_PASSWORD, description={"suggested_value": discovery_info[CONF_PASSWORD]}): str,
                vol.Required(
                    CONF_POLLING_INTERVAL, description={"suggested_value": discovery_info[CONF_POLLING_INTERVAL]}
                ): int,
            }
        )
    else:
        base_schema.update(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(
                    CONF_POLLING_INTERVAL, description={"suggested_value": DEFAULT_POLLING_INTERVAL.total_seconds()},
                ): int,
            }
        )

    return vol.Schema(base_schema)


# pylint: disable=fixme
async def validate_input(user_input: Optional[ConfigType] = None):
    """ TODO """

    # TODO: Check username/password here

    if user_input[CONF_POLLING_INTERVAL] < MIN_POLLING_INTERVAL.total_seconds():
        raise ValueError


class PandoraCasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pandora CAS"""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self.data_schema = {}

    async def async_step_user(self, user_input: Optional[ConfigType] = None):
        errors = {}

        entries = self.hass.config_entries.async_entries(DOMAIN)
        if entries:
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            try:
                await validate_input(user_input)
            except ValueError:
                errors["base"] = "invalid_polling_interval"

            if "base" not in errors:
                username = user_input[CONF_USERNAME]
                return self.async_create_entry(title=username, data=user_input)

        return self.async_show_form(step_id="user", data_schema=_base_schema(), errors=errors)

    async def async_step_discovery(self, discovery_info):
        """Handle discovery."""

        self.data_schema = _base_schema(discovery_info)

        # Check if already configured
        await self.async_set_unique_id(discovery_info[CONF_USERNAME])
        self._abort_if_unique_id_configured()

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(self, user_input: Optional[ConfigType] = None):
        """Confirm discovery."""
        errors = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
            except ValueError:
                errors["base"] = "invalid_polling_interval"

            if "base" not in errors:
                username = user_input[CONF_USERNAME]
                return self.async_create_entry(title=username, data=user_input)

        return self.async_show_form(step_id="discovery_confirm", data_schema=self.data_schema, errors=errors)
