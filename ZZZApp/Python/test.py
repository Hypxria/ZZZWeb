
import os
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, Property
from autogen.settings import url, import_paths

class Backend(QObject):
    dataChanged = Signal()

    def __init__(self):
        super().__init__()
        self._data = int(0.8)
        

    @Property(str, notify=dataChanged)
    def data(self):
        return self._data

    @Slot()
    def updateData(self):
        self._data = "Updated value"
        self.dataChanged.emit()



if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)

    app_dir = Path(__file__).parent.parent

    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    engine.load(os.fspath(app_dir/url))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
