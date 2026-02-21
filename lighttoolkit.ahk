#SingleInstance Force
#UseHook
SetMouseDelay(-1)
SetDefaultMouseSpeed(0)
CoordMode("Mouse", "Client")

utilityMode := 0
sandboxKey := "``"

!t:: {
    global sandboxKey
    IB := InputBox("Enter new sandbox key:", "Sandbox Key", "w200 h100")
    if (IB.Result = "OK" and IB.Value != "")
        sandboxKey := IB.Value
}

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
    ToolTip("alt+o = demote all`nalt+p = kick all`nalt+i = toggle mode`nalt+u = toggle macro active`nalt+y = End script`nalt+t = change sandbox key`nMode: " modeStr "`n3 = spam unknown entity`n4 = spam walls`n5 = whirlpool kill`n6 = spam polygons`n7 = spam heal`n8 = arena size change")
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
    global sandboxKey
    if (utilityMode = 2) {
        SendInput("{" sandboxKey " Down}")
        Loop 50
            SendInput("ch")
        SendInput("{" sandboxKey " Up}")
    } else {
        Send("{" sandboxKey " Down}")
        Loop 20
            Send("ch")
        Send("{" sandboxKey " Up}")
    }
}

4:: {
    global sandboxKey
    if (utilityMode = 2) {
        SendInput("{" sandboxKey " Down}")
        Loop 50
            SendInput("x")
        SendInput("{" sandboxKey " Up}")
    } else {
        Send("{" sandboxKey " Down}")
        Loop 20
            Send("x")
        Send("{" sandboxKey " Up}")
    }
}

5:: {
    global sandboxKey
    if (utilityMode = 2) {
        SendInput("{" sandboxKey " Down}")
        Loop 50
            SendInput("wk")
        SendInput("{" sandboxKey " Up}")
    } else {
        Send("{" sandboxKey " Down}")
        Loop 20
            Send("wk")
        Send("{" sandboxKey " Up}")
    }
}

6:: {
    global sandboxKey
    if (utilityMode = 2) {
        SendInput("{" sandboxKey " Down}")
        Loop 50
            SendInput("f")
        SendInput("{" sandboxKey " Up}")
    } else {
        Send("{" sandboxKey " Down}")
        Loop 20
            Send("f")
        Send("{" sandboxKey " Up}")
    }
}

7:: {
    global sandboxKey
    if (utilityMode = 2) {
        SendInput("{" sandboxKey " Down}")
        Loop 50
            SendInput("h")
        SendInput("{" sandboxKey " Up}")
    } else {
        Send("{" sandboxKey " Down}")
        Loop 20
            Send("h")
        Send("{" sandboxKey " Up}")
    }
}

8:: {
    if (utilityMode = 2)
        SendInput("{Enter}$arena size 2 1024{Enter} {Enter}$arena size 1024 2{Enter}")
    else
        Send("{Enter}$arena size 2 1024{Enter} {Enter}$arena size 1024 2{Enter}")
}

#HotIf
