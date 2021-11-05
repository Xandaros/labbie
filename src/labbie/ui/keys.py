import abc
import asyncio
import dataclasses
import inspect
from typing import ClassVar, List, Union

import injector

from labbie import result
from labbie.ui.system_tray import presenter as system_tray
from labbie.ui.search.window import presenter as search
# from labbie.ui.settings.window import presenter as settings


@dataclasses.dataclass(frozen=True)
class _Key(abc.ABC):
    DELETE_WHEN_CLOSED: ClassVar[bool] = False

    @abc.abstractmethod
    def get_presenter(self, injector: injector.Injector):
        raise NotImplementedError

    def show(self, presenter):
        presenter.show()


@dataclasses.dataclass(frozen=True)
class _PopulatableKey(_Key):
    @abc.abstractmethod
    def _populate_presenter(self, presenter):
        raise NotImplementedError

    def show(self, presenter):
        populate_result = self._populate_presenter(presenter)
        if inspect.iscoroutine(populate_result):
            asyncio.create_task(self._show_after_populate(presenter, populate_result))
        else:
            presenter.show()

    async def _show_after_populate(self, presenter, populate_task):
        await populate_task
        presenter.show()


@dataclasses.dataclass(frozen=True)
class SystemTrayIconKey(_Key):
    def get_presenter(self, injector: injector.Injector):
        return injector.get(system_tray.SystemTrayIconPresenter)


@dataclasses.dataclass(frozen=True)
class SearchWindowKey(_PopulatableKey):
    DELETE_WHEN_CLOSED: ClassVar[bool] = True
    results: Union[None, result.Result, List[result.Result]] = dataclasses.field(default=None, compare=False)

    def get_presenter(self, injector: injector.Injector):
        return injector.get(search.SearchWindowPresenter)

    def _populate_presenter(self, presenter: search.SearchWindowPresenter):
        presenter.populate_view(self.results)


# @dataclasses.dataclass(frozen=True)
# class SettingsWindowKey(_Key):
#     DELETE_WHEN_CLOSED: ClassVar[bool] = True

#     def get_presenter(self, injector: injector.Injector):
#         return injector.get(settings.SettingsWindowPresenter)