#TODO MAKE THIS GENERIC
set (PYTHON_VERSION 3.10)
add_subdirectory(env)

set(PYTHON_ENV_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/env/python-${PYTHON_VERSION})
file(MAKE_DIRECTORY ${PYTHON_ENV_DIRECTORY})

if(WIN32)
    set(PYTHON_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/python.exe)
    set(PYTHON_PIP_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pip.exe)
    set(PYTHON_INSTALLER_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Scripts/pyinstaller.exe)

    #PySide Ui wrapper
    set(PYSIDE_UIC_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Scripts/pyside6-uic.exe)
    #PySide Ressources compiler
    set(PYSIDE_RCC_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Scripts/pyside6-rcc.exe)
    #PySide Translator
    set(PYSIDE_TR_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Scripts/pyside6-lupdate.exe)
    set(PYSIDE_TRQM_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Scripts/pyside6-lrelease.exe)
    set(APP_ICON ${CMAKE_CURRENT_SOURCE_DIR}/resources/icons/OpenIMU.ico)

else(WIN32)
    set(PYTHON_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/python${PYTHON_VERSION})
    set(PYTHON_PIP_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pip)
    set(PYTHON_INSTALLER_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pyinstaller)
    #PySide Ui wrapper
    set(PYSIDE_UIC_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin/pyside6-uic)
    #PySide Ressources compiler
    set(PYSIDE_RCC_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/bin//pyside6-rcc)
    #PySide Translator
    set(PYSIDE_TR_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Scripts/pyside6-lupdate)
    set(PYSIDE_TRQM_EXECUTABLE ${PYTHON_ENV_DIRECTORY}/Scripts/pyside6-lrelease)
    set(APP_ICON ${CMAKE_CURRENT_SOURCE_DIR}/resources/icons/OpenIMU.icns)
endif(WIN32)

#This will generate ui_ files (not needed by python)
SET(uis
    resources/ui/MainWindow.ui
    resources/ui/StartDialog.ui
    resources/ui/ImportDialog.ui
    resources/ui/GroupWidget.ui
    resources/ui/ParticipantWidget.ui
    resources/ui/RecordsetWidget.ui
    resources/ui/ResultWidget.ui
    resources/ui/ImportBrowser.ui
    resources/ui/ExportDialog.ui
    resources/ui/ProcessSelectDialog.ui
    resources/ui/GraphWidget.ui
    resources/ui/DataInfosWidget.ui
    resources/ui/ProgressDialog.ui
    resources/ui/StreamWindow.ui
    resources/ui/ImportMatchDialog.ui
    resources/ui/CrashDialog.ui
    resources/ui/ImportDialogWizard.ui
    resources/ui/TableDataViewWidget.ui
    resources/ui/DataSelector.ui
    resources/ui/DataSelectorDialog.ui
    resources/ui/AboutScreen.ui
)

SET(qrcs
    resources/core.qrc
)

FILE(GLOB srcs "libopenimu/**/*.py")

add_custom_target(uis_target SOURCES ${uis} ${qrcs})

#SET(qml
#    resources/test.qml
#)

file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/resources/ui/python)

# Generate PySide ui files
set(python_uis)
foreach(uifile ${uis})
    message(STATUS "Processing ${uifile}")
    get_filename_component (name_without_extension ${uifile} NAME_WE)
    #Add py extension to file
    set(output_file ${name_without_extension}_ui.py)
    list(APPEND python_uis ${output_file})
    add_custom_target(${output_file}
        COMMAND ${PYSIDE_UIC_EXECUTABLE} ${uifile} -o resources/ui/python/${output_file}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS ${uifile} python-env)
endforeach(uifile)

# Generate PySide resources file
set (python_qrcs)
foreach(rcfile ${qrcs})
    message(STATUS "Processing ${rcfile}")
    get_filename_component (name_without_extension ${rcfile} NAME_WE)
    # Add py extension to file
    set(output_file ${name_without_extension}_rc.py)
    list(APPEND python_qrcs ${output_file})
    add_custom_target(${output_file}
        COMMAND ${PYSIDE_RCC_EXECUTABLE} ${rcfile} -o ${output_file}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS ${rcfile} python-env)
endforeach(rcfile)

# add_custom_target(qml_target SOURCES ${qml})

# Find all python files
file(GLOB_RECURSE libopenimu_python_files libopenimu/*.py)
file(GLOB openimuapp_python_files *.py)

add_custom_target(python_target SOURCES ${libopenimu_python_files} ${openimuapp_python_files})

message(STATUS ${python_files})

# PyInstaller
set (installer_args
    #--hidden-import scipy._lib.messagestream
    #--hidden-import sqlalchemy.ext.baked
    --hidden-import logging.config
#    --exclude-module PySide6.QtQml
#    --exclude-module PySide6.QtQmlModels
#    --exclude-module PySide6.QtQuick3DUtils
#    --exclude-module PySide6.QtSerialPort
#    --exclude-module PySide6.QtVirtualKeyboard
#    --exclude-module PySide6.QtPositioning
#    --exclude-module PySide6.QtWebChannel
#    --exclude-module PySide6.QtWebEngineWidgets
    --clean
    -y
    --windowed # If windowed, no console is displayed
    #--debug
    --icon ${APP_ICON}
)


if(WIN32)
    set (installer_args
        ${installer_args}
        --hidden-import win32api
        #--hidden-import pkg_resources.py2_warn
        --paths ${PYTHON_ENV_DIRECTORY}/Lib/site-packages/scipy/.libs # PyInstaller doesn't seem to find all required DLLs for SciPy...
        --paths ${PYTHON_ENV_DIRECTORY}/Library/bin # PyInstaller doesn't seem to find sqlite3.dll...
    )

    # Build this target to make a package
    add_custom_target(python_package
        COMMAND ${PYTHON_INSTALLER_EXECUTABLE} ${installer_args} ${CMAKE_CURRENT_SOURCE_DIR}/OpenIMU.py
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/alembic.ini ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/alembic ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU/alembic
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS python_target ${python_uis} ${python_qrcs} python-env
    )
endif(WIN32)

if(APPLE)
    set(MACSIGNID "")

    set (installer_args
        ${installer_args}
        --osx-bundle-identifier ca.cdrv.openimu
    )
    # Build this target to make a package
    # set(APPSIGNPATH ${CMAKE_CURRENT_SOURCE_DIR}/dist)

    set (qt_libs
        "Contents/Frameworks/PySide6/Qt/lib/QtCore.framework/Versions/A/QtCore"
        "Contents/Frameworks/PySide6/Qt/lib/QtDBus.framework/Versions/A/QtDBus"
        "Contents/Frameworks/PySide6/Qt/lib/QtGui.framework/Versions/A/QtGui"
        "Contents/Frameworks/PySide6/Qt/lib/QtNetwork.framework/Versions/A/QtNetwork"
        "Contents/Frameworks/PySide6/Qt/lib/QtOpenGL.framework/Versions/A/QtOpenGL"
        "Contents/Frameworks/PySide6/Qt/lib/QtPositioning.framework/Versions/A/QtPositioning"
        "Contents/Frameworks/PySide6/Qt/lib/QtQml.framework/Versions/A/QtQml"
        "Contents/Frameworks/PySide6/Qt/lib/QtQmlModels.framework/Versions/A/QtQmlModels"
        "Contents/Frameworks/PySide6/Qt/lib/QtQuick.framework/Versions/A/QtQuick"
        "Contents/Frameworks/PySide6/Qt/lib/QtWebChannel.framework/Versions/A/QtWebChannel"
        "Contents/Frameworks/PySide6/Qt/lib/QtWebEngineCore.framework/Versions/A/QtWebEngineCore"
    )

    set(sign_libs)
    foreach(lib ${qt_libs})
        list(APPEND sign_libs
            COMMAND codesign --force -s ${MACSIGNID} --deep --options=runtime --timestamp -v ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/${lib}
        )
    endforeach()
    # Sign web engine with specific entitlements
    # Not working correctly for now - fix me - issue is that we are "deep" signing, and thus overwritting the entitlement file.
    # Solution is probably to manually generate a list of files to sign and manually sign them...
    list(APPEND sign_libs
        COMMAND codesign --force -s ${MACSIGNID} --deep --options=runtime --timestamp --entitlements ${CMAKE_CURRENT_SOURCE_DIR}/../setup/QtWebEngineProcess.entitlements -v ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/Frameworks/PySide6/Qt/lib/QtWebEngineCore.framework/Versions/A/Helpers/QtWebEngineProcess.app
        COMMAND codesign --force -s ${MACSIGNID} --deep --options=runtime --timestamp --entitlements ${CMAKE_CURRENT_SOURCE_DIR}/../setup/QtWebEngineProcess.entitlements -v ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/Frameworks/PySide6/Qt/lib/QtWebEngineCore.framework/Versions/A/Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess
    )

    add_custom_target(python_package
        COMMAND ${PYTHON_INSTALLER_EXECUTABLE} ${installer_args} ${CMAKE_CURRENT_SOURCE_DIR}/OpenIMU.py
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/alembic.ini ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/MacOS/
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/alembic ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/MacOS/alembic
        # COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/../setup/qt.conf ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/Resources
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/../setup/Info.plist ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/Info.plist

        # Move Qt libraries in the correct Resource folder, since won't be able to properly sign otherwise

        # Using shell script, since the following lines will do absolute links and not relative ones...
#        COMMAND ${CMAKE_COMMAND} -E rename ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/MacOS/PySide6 ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/Resources/PySide6
#        COMMAND ln -s ../Resources/PySide6 ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/MacOS
#        COMMAND ln -s ../MacOS/Qt* ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/Resources
#        COMMAND ln -s ../MacOS/lib*.dylib ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/Resources

        # Sign executables
        COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/../setup/prepare_to_sign.sh

        # Since webengine isn't working for now, removing from final package to reduce size
        # COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/Frameworks/PySide6/Qt/lib/QtWebEngineCore.framework/Versions/A/QtWebEngineCore
        # COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/MacOS/QtWebEngineCore

        ${sign_libs}
        COMMAND codesign --force -s ${MACSIGNID} --deep --options=runtime --timestamp  -v ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app

        # COMMAND codesign --force -s ${MACSIGNID} --options=runtime --timestamp --entitlements ${CMAKE_CURRENT_SOURCE_DIR}/../setup/QtWebEngineProcess.entitlements -v ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app

#        COMMAND codesign -dvv -v -v ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app
#        COMMAND codesign --force --verify --verbose --sign ${MACSIGNID} --entitlements ${CMAKE_CURRENT_SOURCE_DIR}/../setup/QtWebEngineProcess.entitlements --options=runtime --timestamp -v ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/MacOS/PySide6/Qt/lib/QtWebEngineCore.framework/Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess COMMAND_ECHO STDOUT
#        COMMAND codesign --force --verify --verbose --sign ${MACSIGNID} --options=runtime --timestamp --entitlements ${CMAKE_CURRENT_SOURCE_DIR}/../setup/QtWebEngineProcess.entitlements -v ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.app/Contents/MacOS/OpenIMU COMMAND_ECHO STDOUT

#       # Create dmg file
        # ** Requires create-dmg installed with brew (https://github.com/create-dmg/create-dmg)
        COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/../setup/create_dmg.sh

        COMMAND codesign -s ${MACSIGNID} --options=runtime --timestamp -vvv ${CMAKE_CURRENT_SOURCE_DIR}/dist/OpenIMU.dmg

        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        DEPENDS python_target ${python_uis} ${python_qrcs} python-env
    )

endif(APPLE)

#Translation files, this is done manually to avoid removing the file when doing make clean
# Add -noobsolete parameter to remove obsoleted translations
add_custom_target(openimu_en_ts
    COMMAND ${PYSIDE_TR_EXECUTABLE} -target-language en ${srcs} ${uis} -ts resources/translations/openimu_en.ts -noobsolete
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(openimu_fr_ts
    COMMAND ${PYSIDE_TR_EXECUTABLE} -target-language fr ${srcs} ${uis} -ts resources/translations/openimu_fr.ts -noobsolete
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

#set qm files output directory
set_source_files_properties(${translation_files_srcs} PROPERTIES OUTPUT_LOCATION resources/translations/)

#Build this target to update translations
add_custom_target(translations DEPENDS openimu_en_ts openimu_fr_ts)
add_custom_target(translation_files
    COMMAND ${PYSIDE_TRQM_EXECUTABLE} resources/translations/openimu_en.ts resources/translations/openimu_fr.ts
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    SOURCES ${translation_files_srcs}
)


# Build this target to generate environment and Qt ui/qrc files
add_custom_target(python-all DEPENDS ${python_uis} ${python_qrcs} python-env)
