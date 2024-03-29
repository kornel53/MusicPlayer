import os
import sys
from os.path import expanduser

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *
import exitDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.currentPlaylist = QMediaPlaylist()
        self.currentPlaylist.setPlaybackMode(QMediaPlaylist.Loop)
        self.player = QMediaPlayer()
        self.playBtn = None
        self.pauseBtn = None
        self.stopBtn = None
        self.volumeDownBtn = None
        self.volumeUpBtn = None
        self.prevBtn = QPushButton("Previous song")
        self.nextBtn = QPushButton("Next song")
        self.prevBtn.setEnabled(False)
        self.nextBtn.setEnabled(False)

        self.userAction = -1  # 0 - stopped, 1 - playing,  2 - paused
        self.player.mediaStatusChanged.connect(self.qmp_mediaStatusChanged)
        self.player.mediaChanged.connect(self.qmp_mediaChanged)
        self.player.stateChanged.connect(self.qmp_stateChanged)
        self.player.positionChanged.connect(self.qmp_positionChanged)
        self.player.volumeChanged.connect(self.qmp_volumeChanged)
        self.player.setVolume(20)

        self.songsListWidget = QListWidget()
        self.songsListWidget.doubleClicked.connect(self.songDoubleClicked)

        self.statusBar().showMessage('No Media :: %d' % self.player.volume())
        self.homeScreen()

    def homeScreen(self):
        self.setWindowTitle('Music Player')

        self.createMenubar()
        controlBar = self.addControls()

        centralWidget = QWidget()
        centralWidget.setLayout(controlBar)
        self.setCentralWidget(centralWidget)

        self.resize(200, 600)

        self.show()

    def createMenubar(self):
        menubar = self.menuBar()
        filemenu = menubar.addMenu('File')
        filemenu.addAction(self.fileOpen())
        filemenu.addAction(self.folderOpen())
        filemenu.addAction(self.songInfo())
        filemenu.addAction(self.exitAction())

    def addControls(self):
        controlArea = QVBoxLayout()  # centralWidget
        seekSliderLayout = QHBoxLayout()
        controls = QHBoxLayout()
        playlistCtrlLayout = QHBoxLayout()

        self.playBtn = QPushButton('Play')
        playIcon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.playBtn.setIcon(playIcon)
        self.pauseBtn = QPushButton('Pause')
        pauseIcon = self.style().standardIcon(QStyle.SP_MediaPause)
        self.pauseBtn.setIcon(pauseIcon)
        self.stopBtn = QPushButton('Stop')
        stopIcon = self.style().standardIcon(QStyle.SP_MediaStop)
        self.stopBtn.setIcon(stopIcon)
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.volumeDownBtn = QPushButton()
        volumeDownIcon = QtGui.QIcon(scriptDir + os.path.sep + 'volume_down.png')
        self.volumeDownBtn.setIcon(volumeDownIcon)
        self.volumeUpBtn = QPushButton()
        volumeUpIcon = QtGui.QIcon(scriptDir + os.path.sep + 'volume_up.png')
        self.volumeUpBtn.setIcon(volumeUpIcon)

        # prevBtn = QPushButton('Previous Song')
        prevBtnIcon = self.style().standardIcon(QStyle.SP_MediaSeekBackward)
        self.prevBtn.setIcon(prevBtnIcon)
        # nextBtn = QPushButton('Next Song')
        nextBtnIcon = self.style().standardIcon(QStyle.SP_MediaSeekForward)
        self.nextBtn.setIcon(nextBtnIcon)

        seekSlider = QSlider()
        seekSlider.setMinimum(0)
        seekSlider.setMaximum(100)
        seekSlider.setOrientation(Qt.Horizontal)
        seekSlider.setTracking(True)
        seekSlider.sliderMoved.connect(self.seekPosition)

        seekSliderLabel1 = QLabel('0.00')
        seekSliderLabel2 = QLabel('0.00')
        seekSliderLayout.addWidget(seekSliderLabel1)
        seekSliderLayout.addWidget(seekSlider)
        seekSliderLayout.addWidget(seekSliderLabel2)

        playbackModeGroupBox = QGroupBox('Playback mode')
        sequentialRadioBtn = QRadioButton('Sequential', self)
        randomRadioBtn = QRadioButton('Random', self)
        loopRadioBtn = QRadioButton('Loop', self)

        sequentialRadioBtn.toggled.connect(self.changeToSequential)
        randomRadioBtn.toggled.connect(self.changeToRandom)
        loopRadioBtn.toggled.connect(self.changeToLoop)

        playbackModeLayout = QHBoxLayout()
        playbackModeLayout.addWidget(sequentialRadioBtn)
        playbackModeLayout.addWidget(randomRadioBtn)
        playbackModeLayout.addWidget(loopRadioBtn)
        playbackModeGroupBox.setLayout(playbackModeLayout)

        self.playBtn.clicked.connect(self.playHandler)
        self.pauseBtn.clicked.connect(self.pauseHandler)
        self.stopBtn.clicked.connect(self.stopHandler)
        self.volumeDownBtn.clicked.connect(self.decreaseVolume)
        self.volumeUpBtn.clicked.connect(self.increaseVolume)

        controls.addWidget(self.volumeDownBtn)
        controls.addWidget(self.playBtn)
        controls.addWidget(self.pauseBtn)
        controls.addWidget(self.stopBtn)
        controls.addWidget(self.volumeUpBtn)

        self.prevBtn.clicked.connect(self.prevItemPlaylist)
        self.nextBtn.clicked.connect(self.nextItemPlaylist)
        playlistCtrlLayout.addWidget(self.prevBtn)
        playlistCtrlLayout.addWidget(self.nextBtn)

        controlArea.addLayout(seekSliderLayout)
        controlArea.addLayout(controls)
        controlArea.addLayout(playlistCtrlLayout)
        controlArea.addWidget(self.songsListWidget)
        controlArea.addWidget(playbackModeGroupBox)
        return controlArea

    def playHandler(self):
        self.userAction = 1
        self.playBtn.setEnabled(False)
        self.pauseBtn.setEnabled(True)
        self.statusBar().showMessage('Playing at volume %d' % self.player.volume())
        if self.player.state() == QMediaPlayer.StoppedState:
            if self.player.mediaStatus() == QMediaPlayer.NoMedia:
                print(self.currentPlaylist.mediaCount())
                if self.currentPlaylist.mediaCount() == 0:
                    self.openFile()
                if self.currentPlaylist.mediaCount() != 0:
                    self.player.setPlaylist(self.currentPlaylist)
            elif self.player.mediaStatus() == QMediaPlayer.LoadedMedia:
                self.player.play()
            elif self.player.mediaStatus() == QMediaPlayer.BufferedMedia:
                self.player.play()
        elif self.player.state() == QMediaPlayer.PlayingState:
            pass
        elif self.player.state() == QMediaPlayer.PausedState:
            self.player.play()

    def pauseHandler(self):
        self.userAction = 2
        self.pauseBtn.setEnabled(False)
        self.playBtn.setEnabled(True)
        self.statusBar().showMessage('Paused %s at position %s at volume %d' % \
                                     (self.player.metaData(QMediaMetaData.Title), \
                                      self.centralWidget().layout().itemAt(0).layout().itemAt(0).widget().text(), \
                                      self.player.volume()))
        self.player.pause()

    def stopHandler(self):
        self.userAction = 0
        self.playBtn.setEnabled(True)
        self.pauseBtn.setEnabled(False)
        self.statusBar().showMessage('Stopped at volume %d' % (self.player.volume()))
        if self.player.state() == QMediaPlayer.PlayingState:
            self.stopState = True
            self.player.stop()
        elif self.player.state() == QMediaPlayer.PausedState:
            self.player.stop()
        elif self.player.state() == QMediaPlayer.StoppedState:
            pass

    def qmp_mediaStatusChanged(self):
        if (self.player.mediaStatus() == QMediaPlayer.LoadedMedia or self.player.mediaStatus() == QMediaPlayer.BufferedMedia) and self.userAction == 1:
            durationT = self.player.duration()
            self.centralWidget().layout().itemAt(0).layout().itemAt(1).widget().setRange(0, durationT)
            self.centralWidget().layout().itemAt(0).layout().itemAt(2).widget().setText(
                '%d:%02d' % (int(durationT / 60000), int((durationT / 1000) % 60)))
            self.setCurrentSong(self.currentPlaylist.currentIndex())
            self.player.play()


    def qmp_mediaChanged(self):
        durationT = self.player.duration()
        self.centralWidget().layout().itemAt(0).layout().itemAt(2).widget().setText(
            '%d:%02d' % (int(durationT / 60000), int((durationT / 1000) % 60)))


    def qmp_stateChanged(self):
        if self.player.state() == QMediaPlayer.StoppedState:
            self.player.stop()

    def qmp_positionChanged(self, position, senderType=False):
        sliderLayout = self.centralWidget().layout().itemAt(0).layout()
        if senderType == False:
            sliderLayout.itemAt(1).widget().setValue(position)
        sliderLayout.itemAt(0).widget().setText('%d:%02d' % (int(position / 60000), int((position / 1000) % 60)))

    def seekPosition(self, position):
        sender = self.sender()
        if isinstance(sender, QSlider):
            if self.player.isSeekable():
                self.player.setPosition(position)

    def qmp_volumeChanged(self):
        msg = self.statusBar().currentMessage()
        msg = msg[:-2] + str(self.player.volume())
        self.statusBar().showMessage(msg)

    def increaseVolume(self):
        vol = self.player.volume()
        vol = min(vol + 5, 100)
        self.player.setVolume(vol)

    def decreaseVolume(self):
        vol = self.player.volume()
        vol = max(vol - 5, 0)
        self.player.setVolume(vol)

    def changeToSequential(self):
        self.currentPlaylist.setPlaybackMode(QMediaPlaylist.Sequential)

    def changeToRandom(self):
        self.currentPlaylist.setPlaybackMode(QMediaPlaylist.Random)

    def changeToLoop(self):
        self.currentPlaylist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)

    def clearStyles(self):
        playlistLength = self.songsListWidget.count()
        for i in range(playlistLength):
            self.songsListWidget.item(i).setForeground(Qt.black)

    def fileOpen(self):
        fileAc = QAction('Open File', self)
        fileAc.setShortcut('Ctrl+O')
        fileAc.setStatusTip('Open File')
        fileAc.triggered.connect(self.openFile)
        return fileAc

    def openFile(self):
        fileChoosen = QFileDialog.getOpenFileName(self, 'Open Music File', expanduser('~'), 'Audio (*.mp3 *.ogg *.wav)',
                                                  '*.mp3 *.ogg *.wav')
        if fileChoosen != None:
            fileName = os.path.basename(fileChoosen[0])
            self.currentPlaylist.addMedia(QMediaContent(QUrl.fromLocalFile(fileChoosen[0])))
            newSongItem = QListWidgetItem(fileName)
            self.songsListWidget.addItem(newSongItem)
            if self.currentPlaylist.mediaCount() == 1:
                self.setCurrentSong(0)
            else:
                self.prevBtn.setEnabled(True)
                self.nextBtn.setEnabled(True)


    def folderOpen(self):
        folderAc = QAction('Open Folder', self)
        folderAc.setShortcut('Ctrl+D')
        folderAc.setStatusTip('Open Folder (add all audio files in the folder) ')
        folderAc.triggered.connect(self.addFiles)
        return folderAc

    def addFiles(self):
        folderChoosen = QFileDialog.getExistingDirectory(self, 'Open Music Folder', expanduser('~'))
        if folderChoosen != None:
            it = QDirIterator(folderChoosen)
            it.next()
            oldPlaylistLength = self.currentPlaylist.mediaCount()
            while it.hasNext():
                if it.fileInfo().isDir() == False and it.filePath() != '.':
                    fInfo = it.fileInfo()
                    # print(it.filePath(), fInfo.suffix())
                    if fInfo.suffix() in ('mp3', 'ogg', 'wav'):
                        print('Added file: ', fInfo.fileName())
                        self.currentPlaylist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
                        newSongItem = QListWidgetItem(fInfo.fileName())
                        self.songsListWidget.addItem(newSongItem)
                        if self.currentPlaylist.mediaCount() == 1:
                            self.setCurrentSong(0)
                        else:
                            self.prevBtn.setEnabled(True)
                            self.nextBtn.setEnabled(True)
                it.next()

    def songInfo(self):
        infoAc = QAction('Info', self)
        infoAc.setShortcut('Ctrl+I')
        infoAc.setStatusTip('Displays Current Song Information')
        infoAc.triggered.connect(self.displaySongInfo)
        return infoAc

    def displaySongInfo(self):
        metaDataKeyList = self.player.availableMetaData()
        fullText = '<table border="0">'
        for key in metaDataKeyList:
            value = self.player.metaData(key)
            fullText = fullText + '<tr><td>' + key + '</td><td>' + str(value) + '</td></tr>'
        fullText = fullText + '</table>'
        infoBox = QMessageBox(self)
        infoBox.setWindowTitle('Detailed Song Information')
        infoBox.setTextFormat(Qt.RichText)
        infoBox.setText(fullText)
        infoBox.addButton('OK', QMessageBox.AcceptRole)
        infoBox.show()

    def setCurrentSong(self, index):
        self.songsListWidget.setCurrentRow(index)
        self.clearStyles()
        self.songsListWidget.currentItem().setForeground(Qt.red)

    def prevItemPlaylist(self):
        self.player.playlist().previous()
        if self.currentPlaylist.currentIndex() == -1:
            previousItemIndex = 0
        else:
            previousItemIndex = self.currentPlaylist.currentIndex()
        # print("Current index playlist: ", self.currentPlaylist.currentIndex())
        self.setCurrentSong(previousItemIndex)


    def nextItemPlaylist(self):
        self.player.playlist().next()
        if self.currentPlaylist.currentIndex() == -1:
            nextItemIndex = 0
        else:
            nextItemIndex = self.currentPlaylist.currentIndex()
        # print("Current index playlist: ", self.currentPlaylist.currentIndex())
        self.setCurrentSong(nextItemIndex)

    def songDoubleClicked(self):
        chosenSongIndex = self.songsListWidget.currentRow()
        self.currentPlaylist.setCurrentIndex(chosenSongIndex)
        self.setCurrentSong(chosenSongIndex)

    def exitAction(self):
        exitAc = QAction('&Exit', self)
        exitAc.setShortcut('Ctrl+Q')
        exitAc.setStatusTip('Exit application')
        exitAc.triggered.connect(self.closeEvent)
        return exitAc

    def closeEvent(self, event):
        dialog = exitDialog.ExitDialog()
        result = dialog.exec_()
        if result:
            qApp.quit()
        else:
            try:
                event.ignore()
            except AttributeError:
                pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
