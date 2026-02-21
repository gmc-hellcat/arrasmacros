3::
if (utilityMode = 2) {
    SendInput {] down}
    Loop, 50 {
        SendInput ch
    }
    SendInput {] up}
} else {
    Send {] down}
    Loop, 20 {
        Send ch
    }
    Send {] up}
}
return

4::
if (utilityMode = 2) {
    SendInput {] down}
    Loop, 50 {
        SendInput x
    }
    SendInput {] up}
} else {
    Send {] down}
    Loop, 20 {
        Send x
    }
    Send {] up}
}
return

5::
if (utilityMode = 2) {
    SendInput {] down}
    Loop, 50 {
        SendInput wk
    }
    SendInput {] up}
} else {
    Send {] down}
    Loop, 20 {
        Send wk
    }
    Send {] up}
}
return

6::
if (utilityMode = 2) {
    SendInput {] down}
    Loop, 50 {
        SendInput f
    }
    SendInput {] up}
} else {
    Send {] down}
    Loop, 20 {
        Send f
    }
    Send {] up}
}
return

7::
if (utilityMode = 2) {
    SendInput {] down}
    Loop, 50 {
        SendInput h
    }
    SendInput {] up}
} else {
    Send {] down}
    Loop, 20 {
        Send h
    }
    Send {] up}
}
return

8::
if (utilityMode = 2) {
    SendInput {Enter}$arena size 2 1024{Enter} {Enter}$arena size 1024 2{Enter}
} else {
    Send {Enter}$arena size 2 1024{Enter} {Enter}$arena size 1024 2{Enter}
}
return

#If
