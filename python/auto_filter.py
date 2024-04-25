from python import rsvg
import cairo
import struct
import os


def render_svg_to_png(svg_data):
    svg = rsvg.Handle(data=svg_data)
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, *svg.get_dimension_data())
    ctx = cairo.Context(img)
    svg.render_cairo(ctx)
    return img


struct_pixel = struct.Struct("<I")
pixel_unpack_from = struct_pixel.unpack_from

def read_pixel(x, y, width, height, data):
    if not (0 <= x < width and
            0 <= y < height):
        return 0x00000000
    return pixel_unpack_from(data, (y * width + x) * 4)[0]


class Door:
    def __init__(self, start_x, start_y, color, width, height):
        self.start_x = start_x
        self.start_y = start_y
        self.color = color
        self.width = width
        self.height = height
        self.horizontal = width >= height

    def isPixelInDoor(self, x, y):
        return (self.start_x <= x < self.start_x + self.width and
                self.start_y <= y < self.start_y + self.height)
    
    def isMainDoor(self):
        return self.color == 0xFF727171
    
    def __str__(self):
        return "Door: (%d, %d), [%d, %d], 0x%08X" % (self.start_x, self.start_y, self.width, self.height, self.color)


def validate_path(svg_path):
    with open(svg_path, 'r') as inf:
        svg_data = inf.read()
    return validate_data(svg_data)


def validate_data(svg_data):
    img = render_svg_to_png(svg_data)
    width = img.get_width()
    height = img.get_height()
    data = bytes(img.get_data())

    doors = []
    for y in range(height):
        for x in range(width):
            found = False
            for door in doors:
                if door.isPixelInDoor(x, y):
                    found = True
                    break
            if found:
                continue

            pixel = read_pixel(x, y, width, height, data)
            if pixel == 0xFF727171 or pixel == 0xFFD3A2C7:
                door_start_pixel = (x, y)
                door_color = pixel
                door_width = 1
                for door_x in range(x + 1, width):
                    door_pixel = read_pixel(door_x, y, width, height, data)
                    if door_pixel != door_color:
                        break
                    door_width += 1
                door_height = 1
                for door_y in range(y + 1, height):
                    door_pixel = read_pixel(x, door_y, width, height, data)
                    if door_pixel != door_color:
                        break
                    door_height += 1
                door = Door(*door_start_pixel, door_color, door_width, door_height)
                doors.append(door)

    valid = True
    for door in doors:
        if door.horizontal:
            left_x = door.start_x
            left_y = door.start_y + door.height // 2
            right_x = left_x + door.width - 1
            right_y = left_y
            if (read_pixel(left_x - 1, left_y, width, height, data) != 0xFF000000 or
                read_pixel(right_x + 1, right_y, width, height, data) != 0xFF000000):
                valid = False
                # print("Horizontal", door)
                break
        else:
            top_x = door.start_x + door.width // 2
            top_y = door.start_y
            btm_x = top_x
            btm_y = top_y + door.height - 1
            if (read_pixel(top_x, top_y - 1, width, height, data) != 0xFF000000 or
                read_pixel(btm_x, btm_y + 1, width, height, data) != 0xFF000000):
                valid = False
                # print("Vertical", door)
                break
    return valid and sum(door.isMainDoor() for door in doors) == 1


def main():
    path = input("Enter path: ")

    counts = [0, 0]

    for fname in os.listdir(path):
        svg_path = os.path.join(path, fname)
        if os.path.isfile(svg_path) and fname.endswith(".svg"):
            valid = validate_path(svg_path)
            counts[int(valid)] += 1
            print("%r validity:" % fname, valid)

    print("Invalid count:", counts[0])
    print("Valid count:", counts[1])


if __name__ == '__main__':
    main()
