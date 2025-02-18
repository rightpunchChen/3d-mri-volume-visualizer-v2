DEFAULT_COLORS = {
    "BACKGROUND_COLORS" : (0.82, 0.82, 0.82), # Background color
    "BRAIN_COLORS" : (1.0,0.9,0.9)  ,         # Brain color
    "MASK_COLORS" : {
        1: (1.0, 0.0, 0.0),                   # Label 1 color
        2: (1.0, 1.0, 0.0),                   # Label 2 color
        3: (0.0, 1.0, 0.0),                   # Label 3 color
        4: (0.0, 0.0, 1.0),                   # Label 4 color
        5: (0.0, 1.0, 1.0)                    # Label 5 color
    },
    "PRED_COLORS" : {
        'tp': (0.36, 0.68, 0.68) ,            # True positive color
        'fp': (0.56, 0.1, 1),                 # False positive color
        'fn': (1, 0.5, 0)                     # False negative color
    }
}