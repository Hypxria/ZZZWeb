
import os
import sys
from pathlib import Path

# from PySide6.QtGui import QGuiApplication
# from PySide6.QtQml import QQmlApplicationEngine
# from PySide6.QtCore import QObject, Signal, Slot, Property
# from autogen.settings import url, import_paths

# class Backend(QObject):
#     dataChanged = Signal()

#     def __init__(self):
#         super().__init__()
#         self._data = int(500)
        

#     @Property(str, notify=dataChanged)
#     def data(self):
#         return self._data

#     @Slot()
#     def updateData(self):
#         self._data = "Updated value"
#         self.dataChanged.emit()



# if __name__ == '__main__':
#     app = QGuiApplication(sys.argv)
#     engine = QQmlApplicationEngine()
    
#     backend = Backend()
#     engine.rootContext().setContextProperty("backend", backend)

#     app_dir = Path(__file__).parent.parent

#     engine.addImportPath(os.fspath(app_dir))
#     for path in import_paths:
#         engine.addImportPath(os.fspath(app_dir / path))

#     engine.load(os.fspath(app_dir/url))
#     if not engine.rootObjects():
#         sys.exit(-1)
#     sys.exit(app.exec())

from PySide6.QtCore import QObject, Slot, Property, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from autogen.settings import url, import_paths

class RectangleController(QObject):
    xChanged = Signal()
    yChanged = Signal()
    def __init__(self):
        super().__init__()
        self._x = 29
        self._y = 382

    @Property(int, notify=xChanged)
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if self._x != value:
            self._x = value
            self.xChanged.emit()

    @Property(int, notify=yChanged)
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if self._y != value:
            self._y = value
            self.yChanged.emit()

    @Slot(int, int)
    def moveRectangle(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    controller = RectangleController()
    engine.rootContext().setContextProperty("controller", controller)

    app_dir = Path(__file__).parent.parent

    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    engine.load(os.fspath(app_dir/url))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())