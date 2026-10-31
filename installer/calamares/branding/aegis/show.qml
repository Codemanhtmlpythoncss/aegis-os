/* Aegis installer slideshow — minimal, themeable. Replace text/branding freely. */
import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation {
    id: presentation

    Timer {
        interval: 9000
        running: true
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    function makeSlide(title, body) {
        return { "title": title, "body": body };
    }

    Slide {
        Rectangle { anchors.fill: parent; color: "#14171c" }
        Text {
            anchors.centerIn: parent
            width: parent.width * 0.8
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            color: "#e6e6e6"
            font.pixelSize: 22
            text: "<b>Installing Aegis OS</b><br/><br/>" +
                  "A privacy system that borrows from Tails, Whonix and Qubes — " +
                  "amnesic by default, forced anonymity routing, least privilege."
        }
    }

    Slide {
        Rectangle { anchors.fill: parent; color: "#14171c" }
        Text {
            anchors.centerIn: parent
            width: parent.width * 0.8
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            color: "#e6e6e6"
            font.pixelSize: 22
            text: "<b>Your choices are being applied</b><br/><br/>" +
                  "Network mode (Tor / I2P), your non-Chromium browser, desktop, " +
                  "MAC spoofing and hardening are configured now. Encryption is handled " +
                  "by the partitioning step."
        }
    }

    Slide {
        Rectangle { anchors.fill: parent; color: "#14171c" }
        Text {
            anchors.centerIn: parent
            width: parent.width * 0.8
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            color: "#e6e6e6"
            font.pixelSize: 22
            text: "<b>After install</b><br/><br/>" +
                  "Use <b>Aegis Control</b> to switch network mode or toggle MAC spoofing, " +
                  "and <b>I2P Manager</b> for I2P. Read the threat model — know what this " +
                  "does and does not protect against."
        }
    }
}
