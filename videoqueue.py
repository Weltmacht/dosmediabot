from pyforms.gui.basewidget import BaseWidget
from pyforms.controls   import ControlButton
from pyforms.controls   import ControlList
from pyforms.controls   import ControlCheckBoxList

class VideoQueue(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__('Simple link queue')

        #Definition of the forms fields
        self._queueList  = ControlList("Items", plusFunction  = self.__addBtnAction, minusFunction = self.__rmBtnAction )
        self._queueList.horizontalHeaders = ['This', 'Is', 'a', 'Test']
        self._addButton  = ControlButton('Add')
        self._removeButton  = ControlButton('Remove')

        #Define the event that will be called when the run button is processed
        self._addButton.value = self.addItem
        self._removeButton.value = self.removeItem
        #Define the event called before showing the image in the player
        #self._player.process_frame_event = self.__process_frame

        #Define the organization of the Form Controls
        self._formset = [
            '_queueList',
            '_addButton',
            '_removeButton',
        ]

    def addItem(self):
        """
        Reimplement the addPerson function from People class to update the GUI
        everytime a new person is added.
        """
        self._queueList += ["plop", "plop", "fizz", "fizz"]

    def removeItem(self, index):
        """
        Reimplement the removePerson function from People class to update the GUI
        everytime a person is removed.
        """
        self._queueList -= index

    def __addBtnAction(self):
        """
        Add person button event.
        """
        # A new instance of the PersonWindow is opened and shown to the user.

    def __rmBtnAction(self):
        """
        Remove person button event
        """
        self.removeItem( self._queueList.selected_row_index )


if __name__ == '__main__':

    from pyforms import start_app
    start_app(VideoQueue)
    