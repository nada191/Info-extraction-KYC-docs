import cv2
import easyocr as easyocr
import networkx as nx
import numpy as np


# read the text in the image
def extract_easyocr(image, nbrIter):
    reader = easyocr.Reader(['ar'])

    kernel = np.ones((3, 3), np.uint8)
    image = cv2.erode(image, kernel, iterations=nbrIter)

    #plt.imshow(img)
    result = reader.readtext(image)
    # print(result)
    return result


# order the boxes to read line by line
def order_boxes(res):
    pairs = []

    ###### play with them ######
    threshold_y = 10  # height threshold 10
    threshold_x = 100  # x threshold 100
    ###########################
    # all = []
    for i in range(len(res)):
        for j in range(i + 1, len(res)):
            left_upi, right_upi, right_lowi, left_lowi = res[i][0]
            left_upj, right_upj, right_lowj, left_lowj = res[j][0]
            # first of all, they should be in the same height range, starting Y axis should be almost same
            # their starting x axis is close upto a threshold
            cond1 = (abs(left_upi[1] - left_upj[1]) <= threshold_y)
            cond2 = (abs(right_upi[0] - left_upj[0]) <= threshold_x)
            cond3 = (abs(right_upj[0] - left_upi[0]) <= threshold_x)

            if cond1 and (cond2 or cond3):
                pairs.append([i, j])

    # print('pairs', pairs)
    resclean = res.copy()
    pairsprob = []
    if pairs != []:
        for indxs in pairs:
            pairsprob.append((indxs, min(res[indxs[0]][2], res[indxs[1]][2])))
        # print('pairs avec min de prob', pairsprob)

        g = nx.Graph()
        g.add_edges_from(pairs)
        merged_pairs = [list(a) for a in list(nx.connected_components(g))]
        # print('merged_pairs', merged_pairs)

        for i in merged_pairs:
            for j in i:
                resclean.remove(res[j])

        # for connected components, sort them according to x-axis and merge

        out_final = []

        INF = 999999999  # a large number greater than any co-ordinate
        for idxs in merged_pairs:
            c_bbox = []
            # prob = []
            for i in idxs:
                c_bbox.append(res[i])

            sorted_x = sorted(c_bbox, key=lambda x: x[0][0][0], reverse=True)

            new_sol = {}
            new_sol['description'] = ''

            new_sol['prob'] = min(res[i][2] for i in idxs)  # we will take the minimum of probabilities
            new_sol['vertices'] = [[INF, INF], [-INF, INF], [-INF, -INF], [INF, -INF]]
            # print('sorted_x', sorted_x)
            for k in sorted_x:
                # print('element de sorted_x', k)
                new_sol['description'] += ' ' + str(k[1])

                new_sol['vertices'][0][0] = min(new_sol['vertices'][0][0], k[0][0][0])
                new_sol['vertices'][0][1] = min(new_sol['vertices'][0][1], k[0][0][1])

                new_sol['vertices'][1][0] = max(new_sol['vertices'][1][0], k[0][1][0])
                new_sol['vertices'][1][1] = min(new_sol['vertices'][1][1], k[0][1][1])

                new_sol['vertices'][2][0] = max(new_sol['vertices'][2][0], k[0][2][0])
                new_sol['vertices'][2][1] = max(new_sol['vertices'][2][1], k[0][2][1])

                new_sol['vertices'][3][0] = min(new_sol['vertices'][3][0], k[0][3][0])
                new_sol['vertices'][3][1] = max(new_sol['vertices'][3][1], k[0][3][1])

            out_final.append(new_sol)
        # print('PROBBB', out_final)
        for el in out_final:
            resclean.append([el['vertices'], el['description'], el['prob']])
        # print('resclean', resclean)

    resfinal = sorted(resclean, key=lambda x: x[0][0][1])  # final res, ordered
    # print('cbon', resfinal[0][1])
    # print('resfinal', resfinal)

    return (resfinal)