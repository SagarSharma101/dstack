import json

from fastapi import HTTPException, status

from dstack.api.backend import dict_backends
from dstack.backend.base import CloudBackend
from dstack.hub.db.models import Hub

cache = {}


def get_backend(hub: Hub) -> CloudBackend:
    global cache
    if cache.get(hub.name) is None:
        if hub.config == "":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Empty config for hub = {hub.name}",
            )
        backend = dict_backends(all_backend=True).get(hub.backend)
        if backend is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Backend not found for {hub.backend}",
            )
        configurator = backend.get_configurator()
        if configurator is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Configurator not found for {hub.backend}",
            )
        json_data = json.loads(str(hub.config))
        if hub.auth is not None:
            json_data = json_data | json.loads(str(hub.auth))
        client = configurator.get_backend_client(json_data)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Client dont created for {hub.backend}",
            )
        config = configurator.get_config(json_data)
        backend.__init__(backend_config=config, custom_client=client)
        cache[hub.name] = backend
    return cache.get(hub.name)
