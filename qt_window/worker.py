from PyQt5.QtCore import QObject, pyqtSignal


class ScanWorker(QObject):

    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, scan, output_fname):
        super().__init__()

        self.scan = scan
        self.output_fname = output_fname
        self._abort = False

    def abort(self):
        self._abort = True

    def run(self):

        try:
            self.scan.do_scan(
                self.output_fname,
                progress_callback=self.progress.emit,
                abort_callback=lambda: self._abort
            )

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
