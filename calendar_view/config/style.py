from PIL import ImageFont

arial = 'Arial.ttf'

image_bg = (255, 255, 255, 255)

hour_height = 50
day_width = 400
padding_horizontal = 60
padding_vertical = 30

title_font = ImageFont.truetype(arial, 50)
title_color = 'black'
title_padding_left = 30
title_padding_right = 30
title_padding_top = 30
title_padding_bottom = 20

hour_number_font = ImageFont.truetype(arial, 22)
hour_number_color = 'black'

day_of_week_font = ImageFont.truetype(arial, 28)
day_of_week_color = 'black'

line_day_color = (150, 150, 150, 255)
line_day_width = 5
line_hour_color = (180, 180, 180, 210)
line_hour_width = 2

event_border_width = 4
event_radius = 14
event_border_default = (120, 180, 120, 240)
event_fill_default = (196, 234, 188, 180)

event_name_font = ImageFont.truetype(arial, 36)
event_name_color = 'black'

legend_spacing = 20
legend_padding_top = 40
legend_padding_bottom = 70
legend_padding_left = 70
legend_padding_right = 40
legend_name_font = ImageFont.truetype(arial, 28)
legend_name_color = 'black'

# https://stackoverflow.com/questions/7510313/transparent-png-in-pil-turns-out-not-to-be-transparent
