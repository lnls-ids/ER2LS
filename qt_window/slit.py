import epics
import time


class WBS1():
    """SAPUCAIA WBS1 slit
    """

    def __init__(self):
        self.pv_prefix = 'SPU:A:PP01:'
        self.pv_top = self.pv_prefix + 'E.VAL'
        self.pv_bottom = self.pv_prefix + 'F.VAL'
        self.pv_left = self.pv_prefix + 'G.VAL'
        self.pv_right = self.pv_prefix + 'H.VAL'

        self.pv_top_motor = self.pv_prefix + 'E.CNEN'
        self.pv_bottom_motor = self.pv_prefix + 'F.CNEN'
        self.pv_left_motor = self.pv_prefix + 'G.CNEN'
        self.pv_right_motor = self.pv_prefix + 'H.CNEN'

    # --- properties
    @property
    def top_pos(self):
        return epics.caget(self.pv_top)

    @property
    def bottom_pos(self):
        return epics.caget(self.pv_bottom)

    @property
    def left_pos(self):
        return epics.caget(self.pv_left)

    @property
    def right_pos(self):
        return epics.caget(self.pv_right)

    @property
    def top_enable(self):
        return epics.caget(self.pv_top_motor)

    @property
    def bottom_enable(self):
        return epics.caget(self.pv_bottom)

    @property
    def left_enable(self):
        return epics.caget(self.pv_left)

    @property
    def right_enable(self):
        return epics.caget(self.pv_right)

    # Setters
    def set_top_pos(self, value):
        epics.caput(self.pv_top, value)

    def set_bottom_pos(self, value):
        epics.caput(self.pv_bottom, value)

    def set_left_pos(self, value):
        epics.caput(self.pv_left, value)

    def set_right_pos(self, value):
        epics.caput(self.pv_right, value)

    def set_top_motor(self):
        value = not epics.caget(self.pv_top_motor)
        epics.caput(self.pv_top_motor, value)

    def set_bottom_motor(self):
        value = not epics.caget(self.pv_bottom_motor)
        epics.caput(self.pv_bottom_motor, value)

    def set_left_motor(self):
        value = not epics.caget(self.pv_left_motor)
        epics.caput(self.pv_left_motor, value)

    def set_right_motor(self):
        value = not epics.caget(self.pv_right_motor)
        epics.caput(self.pv_right_motor, value)

    def set_slits_open(self):
        self.set_top_pos(-1.04)
        self.set_bottom_pos(0.58)
        self.set_left_pos(3.30)
        self.set_right_pos(0.12)

    def set_slits_ref(self):
        self.set_top_pos(-0.79)
        self.set_bottom_pos(0.88)
        self.set_left_pos(3.5)
        self.set_right_pos(0.39)

    def set_slits_closed(self):
        self.set_top_pos(-1.04-0.25)
        self.set_bottom_pos(0.58-0.25)
        self.set_left_pos(3.30-0.25)
        self.set_right_pos(0.12-0.25)

    def set_motors(self):
        self.set_bottom_motor()
        self.set_top_motor()
        self.set_left_motor()
        self.set_right_motor()

    def verify_motors_enable(self):
        time.sleep(0.1)
        v1 = epics.caget(self.pv_top_motor)
        v2 = epics.caget(self.pv_bottom_motor)
        v3 = epics.caget(self.pv_left_motor)
        v4 = epics.caget(self.pv_right_motor)
        if v1 and v2 and v3 and v4:
            return True
        else:
            return False


class FOES():
    """SAPUCAIA FOE slit
    """

    def __init__(self):
        self.pv_prefix = 'SPU:A:PP01:'
        self.pv_top = self.pv_prefix + 'B.VAL'
        self.pv_bottom = self.pv_prefix + 'D.VAL'
        self.pv_left = self.pv_prefix + 'C.VAL'
        self.pv_right = self.pv_prefix + 'A.VAL'

        self.pv_top_motor = self.pv_prefix + 'B.CNEN'
        self.pv_bottom_motor = self.pv_prefix + 'D.CNEN'
        self.pv_left_motor = self.pv_prefix + 'C.CNEN'
        self.pv_right_motor = self.pv_prefix + 'A.CNEN'

    # --- properties
    @property
    def top_pos(self):
        return epics.caget(self.pv_top)

    @property
    def bottom_pos(self):
        return epics.caget(self.pv_bottom)

    @property
    def left_pos(self):
        return epics.caget(self.pv_left)

    @property
    def right_pos(self):
        return epics.caget(self.pv_right)

    @property
    def top_enable(self):
        return epics.caget(self.pv_top_motor)

    @property
    def bottom_enable(self):
        return epics.caget(self.pv_bottom)

    @property
    def left_enable(self):
        return epics.caget(self.pv_left)

    @property
    def right_enable(self):
        return epics.caget(self.pv_right)

    def set_top_pos(self, value):
        epics.caput(self.pv_top, value)

    def set_bottom_pos(self, value):
        epics.caput(self.pv_bottom, value)

    def set_left_pos(self, value):
        epics.caput(self.pv_left, value)

    def set_right_pos(self, value):
        epics.caput(self.pv_right, value)

    def set_top_motor(self):
        value = not epics.caget(self.pv_top_motor)
        epics.caput(self.pv_top_motor, value)

    def set_bottom_motor(self):
        value = not epics.caget(self.pv_bottom_motor)
        epics.caput(self.pv_bottom_motor, value)

    def set_left_motor(self):
        value = not epics.caget(self.pv_left_motor)
        epics.caput(self.pv_left_motor, value)

    def set_right_motor(self):
        value = not epics.caget(self.pv_right_motor)
        epics.caput(self.pv_right_motor, value)

    def set_slits_open(self):
        self.set_top_pos(0.7469 + 2.0)
        self.set_bottom_pos(0.3869 + 2.0)
        self.set_left_pos(0.1956 + 2.0)
        self.set_right_pos(0.8446 + 2.0)

    def set_slits_ref(self):
        self.set_top_pos(0.7477)
        self.set_bottom_pos(0.3879)
        self.set_left_pos(0.1893)
        self.set_right_pos(0.8446)

    def set_slits_closed(self):
        self.set_top_pos(0.46)
        self.set_bottom_pos(0.223)
        self.set_left_pos(0.56)
        self.set_right_pos(-0.095)

    def set_motors(self):
        self.set_bottom_motor()
        self.set_top_motor()
        self.set_left_motor()
        self.set_right_motor()

    def verify_motors_enable(self):
        time.sleep(0.1)
        v1 = epics.caget(self.pv_top_motor)
        v2 = epics.caget(self.pv_bottom_motor)
        v3 = epics.caget(self.pv_left_motor)
        v4 = epics.caget(self.pv_right_motor)
        if v1 and v2 and v3 and v4:
            return True
        else:
            return False
