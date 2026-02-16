#Requires AutoHotkey v2.0
;you can change your tank center coordinates. find it using autohotkey dash
; assistance for using anni in close quarters. Automatically aligns your tanks barrels to exact verical or horizontal, whichever is closest when leftalt or rightalt is clicked.
tankX := 960 ;preset
tankY := 570 ; preset 
isHolding := false
targetX := 0
targetY := 0

LAlt::
RAlt::
{
    global tankX, tankY, isHolding, targetX, targetY
    
    if (isHolding)
        return
    
    MouseGetPos(&mouseX, &mouseY)
    
    ; Calculate the angle from tank center to mouse
    deltaX := mouseX - tankX
    deltaY := mouseY - tankY
    
    distance := Sqrt(deltaX**2 + deltaY**2)
    
    ; If mouse is too close to center, don't move it
    if (distance < 10)
        return
    
    absAngleX := Abs(deltaX)
    absAngleY := Abs(deltaY)
    
    if (absAngleY < absAngleX) {
        targetX := mouseX
        targetY := tankY
    } else {
        targetX := tankX
        targetY := mouseY
    }
    
    MouseMove(targetX, targetY, 0)
    
    isHolding := true
    
    SetTimer(HoldPosition, 10)
    SetTimer(ReleaseHold, -300);can change the hold duration
}

HoldPosition()
{
    global targetX, targetY, isHolding
    if (isHolding)
        MouseMove(targetX, targetY, 0)
}

ReleaseHold()
{
    global isHolding
    isHolding := false
    SetTimer(HoldPosition, 0)
}
