#!/usr/bin/env python

from scad import *

class BeltArm(SCAD_Object):
    arm_length = 40
    arm_width = 10
    arm_depth = 2
    bolt_dia = 4.4
    standoff_dia = 8
    standoff_height = 1.5
    belt_hole_height = 7.1
    belt_hole_width = 2.5
    belt_hole_offset = 3

    def scad(self):
        arm = Cube(x=self.arm_length, y=self.arm_width, z=self.arm_depth, center=True)
        standoff = Cylinder(dia=self.standoff_dia, h=self.standoff_height, center=True)
        standoff = Translate(z=(self.arm_depth + self.standoff_height) / 2.0)(standoff)
        arm = Union()(arm, standoff)
        bolt = Cylinder(dia=self.bolt_dia, h=20, center=True)
        belt_hole = Cube(x=self.belt_hole_width, y=self.belt_hole_height, z=self.arm_depth + 1, center=True)
        belt_hole1 = Translate(x=(self.belt_hole_width - self.arm_length) / 2.0 + self.belt_hole_offset)(belt_hole)
        belt_hole2 = Translate(x=(self.belt_hole_width - self.arm_length) / -2.0 - self.belt_hole_offset)(belt_hole)
        arm = Difference()(arm, bolt, belt_hole1, belt_hole2)
        cone = Cylinder(dia1=self.standoff_dia, dia2=self.standoff_dia - .5, h=self.arm_depth / 2.0, center=True)
        cone = Translate(z=-.51)(cone)
        arm = Difference()(arm, cone)
        return arm

class Spindle(SCAD_Object):
    # XXX: bearing hole is a little loose
    belt_width = 6
    spindle_height = belt_width + 2.5
    spindle_thickness = 2
    bearing_height = 5
    bearing_diameter = 16
    spindle_diameter = bearing_diameter + 0.5
    shoulder_height = 1
    shoulder_diameter = spindle_diameter + spindle_thickness + 5
    ring_height = .4
    ring_diameter = spindle_diameter - 1

    @property
    def bearing(self):
        return Cylinder(dia=self.bearing_diameter, h=self.bearing_height, center=True)

    @property
    def spindle(self):
        body = Pipe(id=self.spindle_diameter, od=self.spindle_diameter + self.spindle_thickness, h=self.spindle_height, center=True)
        shoulder_cap = Pipe(id=self.spindle_diameter, od=self.shoulder_diameter, h=self.shoulder_height / 2.0, center=True)
        shoulder_cap1 = Translate(z=self.shoulder_height / 2.0)(shoulder_cap)
        shoulder1 = Pipe(id=self.spindle_diameter, od1=self.spindle_diameter + self.spindle_thickness, od2=self.shoulder_diameter, h=self.shoulder_height / 2.0, center=True)
        shoulder1 = Union()(shoulder1, shoulder_cap1)
        shoulder1 = Translate(z=(self.spindle_height - self.shoulder_height) / 2.0)(shoulder1)

        shoulder2 = Pipe(id=self.spindle_diameter, od2=self.spindle_diameter + self.spindle_thickness, od1=self.shoulder_diameter, h=self.shoulder_height / 2.0, center=True)
        shoulder_cap2 = Translate(z=self.shoulder_height / -2.0)(shoulder_cap)
        shoulder2 = Union()(shoulder2, shoulder_cap2)
        shoulder2 = Translate(z=(self.spindle_height - self.shoulder_height) / -2.0)(shoulder2)

        body = Union()(body, shoulder1, shoulder2)
        chamfer1 = Pipe(id=self.spindle_diameter, od1=self.spindle_diameter, od2=self.spindle_diameter + 1, h=1, center=True)
        chamfer1 = translate(z=self.spindle_height / 2.0)(chamfer1)
        chamfer2 = Pipe(id=self.spindle_diameter, od2=self.spindle_diameter, od1=self.spindle_diameter + 1, h=1, center=True)
        chamfer2 = translate(z=self.spindle_height / -2.0)(chamfer2)
        body = Render()(Difference()(body, chamfer1, chamfer2))
        #ring = Pipe(id=self.ring_diameter, od=self.spindle_diameter + self.spindle_thickness, h=self.ring_height, center=True)
        #return Union()(body, shoulder1, shoulder2, ring)
        return body
    
    def scad(self):
        return self.spindle

class MotorMount(SCAD_Object):
    height = 15
    depth = 78
    thickness = 2
    plate_height = 40
    motor_mount_screw_dia = 3.5
    motor_mount_slide_length = 10
    nema17_bolt_distance = 31
    nema17_center_hole_dia = 25
    mount_bolt_distance = 55
    mount_bolt_dia = 4
    mount_bolt_height_offset = 0
    motor_dugout = 42
    width = mount_bolt_distance + mount_bolt_dia + thickness + 4
    pully_bolt_dia = 5.1

    def motor_holes(self):
        hdis = self.nema17_bolt_distance / 2.0
        h1 = Cylinder(dia=self.motor_mount_screw_dia, h=self.height * 2, center=True)
        h2 = Translate(y=self.motor_mount_slide_length)(h1)
        hole = Hull()(h1, h2)
        holes = []
        for x_offset in [hdis, -hdis]:
            for y_offset in [hdis, -hdis]:
                holes.append(Translate(x=x_offset, y=y_offset)(hole))
        center_hole_1 = Cylinder(dia=self.nema17_center_hole_dia, h=self.height * 2, center=True)
        center_hole_2 = Translate(y=self.motor_mount_slide_length)(center_hole_1)
        center_hole = Hull()(center_hole_1, center_hole_2)
        holes.append(center_hole)
        holes = Union()(*holes)
        return holes

    def scad(self):
        mount = Cube(x=self.width, y=self.depth, z=self.height, center=True)
        # dugout
        dugout = Cube(x=self.motor_dugout, y=self.depth-20, z=self.height - self.thickness, center=True)
        dugout = Translate(z=-self.thickness, y=-self.thickness + 8)(dugout)
        mount = Difference()(mount, dugout)
        mount = Translate(y=self.depth / -2.0)(mount)
        holes = self.motor_holes()
        holes = Translate(y=-35)(holes)
        mount = Difference()(mount, holes)
        mount = Translate(z=self.height / -2.0)(mount)
        # pulley holes
        pully_bolt = Cylinder(dia=self.pully_bolt_dia, h=self.height * 2, center=True)
        pully_bolt1 = Translate(x=-23.85, y=-70)(pully_bolt)
        pully_bolt2 = Translate(x=23.85, y=-70)(pully_bolt)
        mount = Difference()(mount, pully_bolt1, pully_bolt2)
        # mount bolts
        bolt = Cylinder(dia=self.mount_bolt_dia, h=50, center=True)
        bolt = Rotate(x=90)(bolt)
        bolt = Union()(bolt)
        bolt = Translate(z=self.motor_mount_screw_dia / -2.0 - self.thickness)(bolt)
        _side = 8.5
        bolt_shroud = Cube(x=_side + 2,  y=self.depth-20, z=self.height, center=True)
        bolt_shroud_1 = Translate(y=self.depth / -2.0 - self.thickness - 1 + 9, x=-(self.width - _side) / 2.0, z=self.height / -2.0)(bolt_shroud)
        bolt_shroud_2 = Translate(y=self.depth / -2.0 - self.thickness - 1 + 9, x=(self.width - _side) / 2.0, z=self.height / -2.0)(bolt_shroud)

        bolt1 = Translate(x=self.mount_bolt_distance / 2.0)(bolt)
        bolt2 = Translate(x=self.mount_bolt_distance / -2.0)(bolt)
        bolts = Union()(bolt1, bolt2)
        bolts = Translate(z=self.mount_bolt_height_offset - 1)(bolts)
        bolts = Union()(bolts, bolt_shroud_1, bolt_shroud_2)
        body = Render()(Difference()(mount, bolts))
        return body

class IdleMount(MotorMount):
    height = 10
    depth = 24
    thickness = 2
    plate_height = 40
    motor_mount_screw_dia = 3.5
    motor_mount_slide_length = 10
    nema17_bolt_distance = 31
    nema17_center_hole_dia = 25
    mount_bolt_distance = 55
    mount_bolt_dia = 4.1
    mount_bolt_height_offset = 0
    motor_dugout = 42
    width = mount_bolt_distance + mount_bolt_dia + thickness + 4
    pully_bolt_dia = 5.1

    def scad(self):
        mount = Cube(x=self.width, y=self.depth, z=self.height, center=True)
        mount = Translate(y=self.depth / -2.0)(mount)
        mount = Translate(z=self.height / -2.0)(mount)
        # pulley holes
        pully_bolt = Cylinder(dia=self.pully_bolt_dia, h=self.height * 2, center=True)
        pully_bolt1 = Translate(x=-23.85, y=-12)(pully_bolt)
        pully_bolt2 = Translate(x=23.85, y=-12)(pully_bolt)
        # mount bolts
        bolt_len = 55
        head_len = 25
        bolt = Cylinder(dia=self.mount_bolt_dia, h=bolt_len, center=True)
        bolt_head = Cylinder(dia=self.mount_bolt_dia + 3.1, h=head_len, center=True)
        bolt_head = Translate(z=(bolt_len - head_len) / 2.0)(bolt_head)
        bolt = Union()(bolt_head, bolt)
        bolt = Rotate(x=90)(bolt)
        bolt = Union()(bolt)
        bolt = Translate(z=self.motor_mount_screw_dia / -2.0 - self.thickness)(bolt)
        bolt1 = Translate(x=self.mount_bolt_distance / 2.0, z=self.mount_bolt_height_offset - 1)(bolt)
        bolt2 = Translate(x=self.mount_bolt_distance / -2.0, z=self.mount_bolt_height_offset - 1)(bolt)
        bolts = Union()(bolt1, bolt2, pully_bolt1, pully_bolt2)
        body = Render()(Difference()(mount, bolts))
        return body

low_res = SCAD_Globals(fn=20)
high_res = SCAD_Globals(fn=60)

arm = BeltArm()
arm_scad = low_res(arm)
arm_stl = high_res(arm)
arm_scad.render("belt_arm.scad")
arm_stl.render("belt_arm.stl")

im = IdleMount()
im_scad = low_res(im)
im_stl = high_res(im)
im_scad.render("idle_mount.scad")
#im_stl.render("idle_mount.stl")

mm = MotorMount()
mm_scad = low_res(mm)
mm_stl = high_res(mm)
mm_scad.render("motor_mount.scad")
#mm_stl.render("motor_mount.stl")

spindle = Spindle()
spindle_scad = low_res(spindle)
spindle_stl = high_res(spindle)
spindle_scad.render("spindle.scad")
#spindle_stl.render("spindle.stl")
