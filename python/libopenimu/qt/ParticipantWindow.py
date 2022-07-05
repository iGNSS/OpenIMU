from PySide6.QtCore import Qt, Slot

from resources.ui.python.ParticipantWidget_ui import Ui_frmParticipant
from libopenimu.models.Participant import Participant
from libopenimu.qt.DataEditor import DataEditor


class ParticipantWindow(DataEditor):

    participant = Participant()
    dbMan = None
    editMode = False  # Set to true if the edit button behavior is required

    def __init__(self, db_manager, participant=None, parent=None, default_group=None, edit_mode=False):
        super().__init__(parent=parent)
        self.UI = Ui_frmParticipant()
        self.UI.setupUi(self)

        self.participant = participant
        self.dbMan = db_manager
        self.data_type = "participant"

        # Setup editing UI
        self.editMode = edit_mode
        self.UI.btnEdit.setVisible(self.editMode)
        self.UI.frameButtons.setVisible(not self.editMode)
        self.UI.frameData.setEnabled(not self.editMode)

        # Signals / Slots connections
        self.UI.btnCancel.clicked.connect(self.cancel_clicked)
        self.UI.btnSave.clicked.connect(self.save_clicked)
        self.UI.txtName.textEdited.connect(self.name_edited)
        self.UI.txtDesc.textChanged.connect(self.desc_edited)
        self.UI.cmbGroups.currentIndexChanged.connect(self.group_edited)
        self.UI.btnEdit.clicked.connect(self.edit_clicked)

        # Load groups
        groups = self.dbMan.get_all_groups()
        self.UI.cmbGroups.clear()
        self.UI.cmbGroups.addItem(self.tr('None'), userData=None)

        for group in groups:
            self.UI.cmbGroups.addItem(group.name, userData=group.id_group)

        # Update data
        self.update_data()

        # Set default group for new participants
        if default_group is not None:
            self.UI.cmbGroups.setCurrentIndex(self.UI.cmbGroups.findData(default_group.id_group, Qt.UserRole))

        self.enable_buttons(False)

    def validate(self):
        rval = True
        if self.UI.txtName.text() == '':
            self.UI.txtName.setStyleSheet('background-color: #ffcccc;')
            rval = False
        else:
            self.UI.txtName.setStyleSheet('')

        if self.UI.cmbGroups.currentIndex == -1:
            rval = False

        return rval

    def update_data(self):
        if self.participant is not None:
            self.UI.txtName.setText(self.participant.name)
            self.UI.txtDesc.setPlainText(self.participant.description)
            # if self.participant.group is not None and self.participant.group.name is not None:
            #     self.UI.lblGroupValue.setText(self.participant.group.name)
            # else:
            #     self.UI.lblGroupValue.setText("Aucun")
            self.UI.cmbGroups.setCurrentIndex(self.UI.cmbGroups.findData(self.participant.id_group))
        else:
            self.UI.txtName.setText("")
            self.UI.txtDesc.setPlainText("")
            self.UI.cmbGroups.setCurrentIndex(0)
        self.validate()

    def enable_buttons(self, enable):
        self.UI.btnCancel.setEnabled(enable or self.participant is None or self.editMode)
        self.UI.btnSave.setEnabled(enable)

    def update_modified_status(self):
        self.enable_buttons(
                            (self.participant is not None and self.UI.txtName.text() != self.participant.name) or
                            (self.participant is None and self.UI.txtName.text() != "") or
                            (self.participant is not None and self.UI.txtDesc.toPlainText() != self.participant.description) or
                            (self.participant is None and self.UI.txtDesc.toPlainText() != "") or
                            (self.participant is not None and self.UI.cmbGroups.currentData() != self.participant.id_group)
                            )
        self.validate()

    @Slot()
    def save_clicked(self):
        if self.validate():
            if self.participant is None:
                self.participant = Participant()
            self.participant.name = self.UI.txtName.text()
            self.participant.description = self.UI.txtDesc.toPlainText()
            self.participant.id_group = self.UI.cmbGroups.currentData()
            self.participant = self.dbMan.update_participant(self.participant)
            self.enable_buttons(False)
            self.dataSaved.emit()

            if self.editMode:
                self.UI.btnEdit.show()
                self.UI.frameButtons.hide()
                self.UI.frameData.setEnabled(False)
                self.dataEditing.emit(False)

    @Slot()
    def cancel_clicked(self):
        self.update_data()
        self.dataCancelled.emit()
        if self.editMode:
            self.UI.btnEdit.show()
            self.UI.frameButtons.hide()
            self.UI.frameData.setEnabled(False)
            self.dataEditing.emit(False)

    @Slot(str)
    def name_edited(self, new_value):
        self.update_modified_status()

    @Slot()
    def desc_edited(self):
        self.update_modified_status()

    @Slot()
    def group_edited(self):
        self.update_modified_status()

    @Slot()
    def edit_clicked(self):
        if self.UI.btnEdit.isVisible():
            self.UI.btnEdit.hide()
            self.UI.frameButtons.show()
            self.UI.frameData.setEnabled(True)
            self.dataEditing.emit(True)
