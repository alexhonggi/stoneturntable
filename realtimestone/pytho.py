    accumulated_pixel_color = 0
    
    if frame_cnt % leap == 0:
        for i in range(h): 
            # Exception: Increase accumulated_pixel_color if it is not the last pixel of the frame
            if (i != h-1) and ((i % num_area) != (num_area - 1)):
                accumulated_pixel_color += (255 - roi_gray[i][0])

            # Process accumulated_pixel_color if it is the last pixel of the frame
            if (i == h-1) or ((i % num_area) == (num_area - 1)):
                cnt = i % num_area if i == h-1 else num_area

                if (accumulated_pixel_color // cnt) < bound:
                    accumulated_pixel_color = cnt * bound

                avg_color = accumulated_pixel_color // cnt
                magnitude.append(avg_color)
                frame_num.append(frame_cnt)
                accumulated_pixel_color = 0