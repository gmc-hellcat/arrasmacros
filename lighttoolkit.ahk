#SingleInstance Force
SetMouseDelay(-1)
SetDefaultMouseSpeed(0)
CoordMode("Mouse", "Client")

utilityMode := 0

!u:: {
    Suspend(-1)
    if A_IsSuspended
        ToolTip("Macro SUSPENDED")
    else
        ToolTip("Macro ACTIVE")
    SetTimer(() => ToolTip(), -2000)
}

!y:: ExitApp()

!h:: {
    if (utilityMode = 0)
        modeStr := "OFF"
    else if (utilityMode = 1)
        modeStr := "SLOW"
    else
        modeStr := "FAST"
    ToolTip("alt+o = demote all`nalt+p = kick all`nalt+i = toggle mode`nalt+u = toggle macro active`nalt+y = End script`nMode: " modeStr "`n3 = spam unknown entity`n4 = spam walls`n5 = whirlpool kill`n6 = spam polygons`n7 = spam heal`n8 = arena size change")
    SetTimer(() => ToolTip(), -5000)
}

!p:: {
    Loop 14 {
        y := 259 + (A_Index - 1) * 45
        Click(440, y)
    }
    SendInput("{WheelDown 100}")
    Sleep(50)
    Loop 14 {
        y := 259 + (A_Index - 1) * 45
        Click(440, y)
    }
}

!o:: {
    Loop 14 {
        y := 256 + (A_Index - 1) * 45
        Click(405, y)
        Click(405, y)
        Click(405, y)
    }
    SendInput("{WheelDown 100}")
    Sleep(50)
    Loop 14 {
        y := 256 + (A_Index - 1) * 45
        Click(405, y)
        Click(405, y)
        Click(405, y)
    }
}

!i:: {
    global utilityMode
    utilityMode := utilityMode + 1
    if (utilityMode > 2)
        utilityMode := 0
    if (utilityMode = 0)
        ToolTip("Utility Mode: OFF")
    else if (utilityMode = 1)
        ToolTip("Utility Mode: SLOW")
    else if (utilityMode = 2)
        ToolTip("Utility Mode: FAST")
    SetTimer(() => ToolTip(), -2000)
}

#HotIf utilityMode > 0

3:: {
    if (utilityMode = 2) {
        SendInput("{] down}")
        Loop 50
            SendInput("ch")
        SendInput("{] up}")
    } else {
        Send("{] down}")
        Loop 20
            Send("ch")
        Send("{] up}")
    }
}

4:: {
    if (utilityMode = 2) {
        SendInput("{] down}")
        Loop 50
            SendInput("x")
        SendInput("{] up}")
    } else {
        Send("{] down}")
        Loop 20
            Send("x")
        Send("{] up}")
    }
}

5:: {
    if (utilityMode = 2) {
        SendInput("{] down}")
        Loop 50
            SendInput("wk")
        SendInput("{] up}")
    } else {
        Send("{] down}")
        Loop 20
            Send("wk")
        Send("{] up}")
    }
}

6:: {
    if (utilityMode = 2) {
        SendInput("{] down}")
        Loop 50
            SendInput("f")
        SendInput("{] up}")
    } else {
        Send("{] down}")
        Loop 20
            Send("f")
        Send("{] up}")
    }
}

7:: {
    if (utilityMode = 2) {
        SendInput("{] down}")
        Loop 50
            SendInput("h")
        SendInput("{] up}")
    } else {
        Send("{] down}")
        Loop 20
            Send("h")
        Send("{] up}")
    }
}

8:: {
    if (utilityMode = 2)
        SendInput("{Enter}$arena size 2 1024{Enter} {Enter}$arena size 1024 2{Enter}")
    else
        Send("{Enter}$arena size 2 1024{Enter} {Enter}$arena size 1024 2{Enter}")
}

#HotIf
