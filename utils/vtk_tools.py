import os
import vtk
import numpy as np
import vtkmodules.util.numpy_support as vtkutil

def check_files(file):
    if os.path.exists(file):
        return 1
    else:
        return 0

def check_label(label, label_value):
    if label_value in label:
        return 0
    else:
        return 1
    
def load_image(file_name):
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(file_name)
    reader.Update()
    return reader.GetOutput()

def vtk_img_to_numpy(vtk_img):
    dims = vtk_img.GetDimensions()
    vtk_array = vtk_img.GetPointData().GetScalars()
    np_array = vtkutil.vtk_to_numpy(vtk_array)
    np_array = np_array.reshape(dims[2], dims[1], dims[0])  # Reshape according to the VTK image dimensions
    return np_array

def numpy_to_vtk_img(np_array, reference_vtk_img):
    vtk_img = vtk.vtkImageData()
    vtk_img.DeepCopy(reference_vtk_img)  # Copy spatial info (dimensions, spacing, origin, etc.)
    
    vtk_data_array = vtkutil.numpy_to_vtk(np_array.ravel(), deep=True, array_type=vtk.VTK_UNSIGNED_CHAR)
    vtk_img.GetPointData().SetScalars(vtk_data_array)
    
    return vtk_img

def create_contour(vtk_img, label_value=None):
    # itk_img = itk.imread(filename=file_name)
    # vtk_img = itk.vtk_image_from_image(l_image=itk_img)
    contour = vtk.vtkDiscreteMarchingCubes()
    contour.SetInputData(vtk_img)
    if label_value:
        contour.SetValue(0, label_value)
    return contour

def create_smoother(contour):
    smoother = vtk.vtkSmoothPolyDataFilter()
    smoother.SetInputConnection(contour.GetOutputPort())
    smoother.SetNumberOfIterations(500)
    return smoother


def create_normals(smoother):
    brain_normals = vtk.vtkPolyDataNormals()
    brain_normals.SetInputConnection(smoother.GetOutputPort())
    brain_normals.SetFeatureAngle(60.0)
    return brain_normals


def create_mapper(normals):
    brain_mapper = vtk.vtkPolyDataMapper()
    brain_mapper.SetInputConnection(normals.GetOutputPort())
    brain_mapper.ScalarVisibilityOff()
    brain_mapper.Update()
    return brain_mapper

def create_property(opacity, color):
    prop = vtk.vtkProperty()
    prop.SetColor(color[0], color[1], color[2])
    prop.SetOpacity(opacity)
    return prop


def create_actor(mapper, prop):
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetProperty(prop)
    return actor

def setup_actor(img, opacity=0.3, color=(1.0,0.9,0.9), label_value=None):
    # img = reader(file_name)
    contour = create_contour(img, label_value)
    smoother = create_smoother(contour)
    normals = create_normals(smoother)
    actor_mapper = create_mapper(normals)
    actor_property = create_property(opacity, color)
    actor = create_actor(actor_mapper, actor_property)
    return actor

def creat_reslice(vtk_img, orientation_mat):
    reslice = vtk.vtkImageReslice()
    reslice.SetInputData(vtk_img)
    reslice.SetOutputDimensionality(2)
    reslice.SetInterpolationModeToLinear()
    reslice.SetResliceAxes(orientation_mat)
    reslice.Update()
    return reslice

def create_mapper_sv(reslice):
    brain_mapper = vtk.vtkImageMapper()
    brain_mapper.SetInputConnection(reslice.GetOutputPort())
    brain_mapper.SetColorWindow(1000)
    brain_mapper.SetColorLevel(500)
    brain_mapper.Update()
    return brain_mapper

def create_actor_sv(mapper):
    actor = vtk.vtkActor2D()
    actor.SetMapper(mapper)
    return actor

def setup_actor_sv(vtk_img, orientation):
    matrix = vtk.vtkMatrix4x4()

    if orientation == 0:        # (XY)
        matrix.DeepCopy((1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1))

    elif orientation == 1:   # (YZ)
        matrix.DeepCopy((0, 0, 1, 0,
                        0, 1, 0, 0,
                        -1, 0, 0, 0,
                        0, 0, 0, 1))

    elif orientation == 2:    # (XZ)
        matrix.DeepCopy((1, 0, 0, 0,
                        0, 0, 1, 0,
                        0, 1, 0, 0,
                        0, 0, 0, 1))

    reslice = creat_reslice(vtk_img, matrix)
    # mapper = create_mapper_sv(reslice)
    # actor = create_actor_sv(mapper)
    actor = vtk.vtkImageActor()
    actor.GetMapper().SetInputConnection(reslice.GetOutputPort())
    return reslice, actor

def setup_label_actor_sv(label_image, orientation, selected_labels, colors, alpha):
    matrix = vtk.vtkMatrix4x4()

    if orientation == 0:        # (XY)
        matrix.DeepCopy((1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1))

    elif orientation == 1:   # (YZ)
        matrix.DeepCopy((0, 0, 1, 0,
                        0, 1, 0, 0,
                        -1, 0, 0, 0,
                        0, 0, 0, 1))

    elif orientation == 2:    # (XZ)
        matrix.DeepCopy((1, 0, 0, 0,
                        0, 0, 1, 0,
                        0, 1, 0, 0,
                        0, 0, 0, 1))

    label_reslice = vtk.vtkImageReslice()
    label_reslice.SetInputData(label_image)
    label_reslice.SetInterpolationModeToNearestNeighbor()
    label_reslice.SetOutputDimensionality(2)
    label_reslice.SetResliceAxes(matrix)
    label_reslice.Update()

    label_map = vtk.vtkImageMapToColors()
    label_map.SetInputConnection(label_reslice.GetOutputPort())
    label_map.SetLookupTable(create_label_lut(colors, alpha, selected_labels))
    label_map.SetOutputFormatToRGBA()
    
    label_map.Update()
    actor = vtk.vtkImageActor()
    actor.GetMapper().SetInputConnection(label_map.GetOutputPort())
    return label_reslice, actor

def create_label_lut(colors, alpha, selected_labels=None):
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfColors(6)
    lut.SetTableRange(0, 6)
    lut.Build()
    lut.SetTableValue(0, 0, 0, 0, 0)

    if selected_labels:
        for i in range(1, 6):
            if i in selected_labels:
                r, g, b = colors[i][0], colors[i][1], colors[i][2]
                lut.SetTableValue(i, r, g, b, alpha)
            else:
                lut.SetTableValue(i, 0, 0, 0, 0)
    else:
        r, g, b = colors[0], colors[1], colors[2]
        lut.SetTableValue(1, r, g, b, alpha)
    
    return lut

def set_camera(renderer):
    camera = renderer.GetActiveCamera()
    camera.SetPosition(0, -10, 0) 
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)
    renderer.ResetCamera()

def set_camera_sv(renderer):
    camera = renderer.GetActiveCamera()
    camera.SetPosition(0, 0, 1)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 1, 0)
    renderer.ResetCamera()

def AND(vtk_img1, vtk_img2):
    np_img1 = vtk_img_to_numpy(vtk_img1)
    np_img2 = vtk_img_to_numpy(vtk_img2)
    
    and_result = np.logical_and(np_img1, np_img2).astype(np.uint8)
    if not np.any(and_result):
        return None
    
    vtk_result_img = numpy_to_vtk_img(and_result, vtk_img1)
    return vtk_result_img

def XOR(vtk_img1, vtk_img2):
    np_img1 = vtk_img_to_numpy(vtk_img1)
    np_img2 = vtk_img_to_numpy(vtk_img2)
    
    xor_result = np.logical_xor(np_img1, np_img2).astype(np.uint8)
    if not np.any(xor_result):
        return None
    
    vtk_result_img = numpy_to_vtk_img(xor_result, vtk_img1)
    return vtk_result_img

def false_positive(gt_vtk_img, pred_vtk_img):
    gt_np_img = vtk_img_to_numpy(gt_vtk_img)
    pred_np_img = vtk_img_to_numpy(pred_vtk_img)
    
    false_positive_result = np.logical_and(np.logical_not(gt_np_img), pred_np_img).astype(np.uint8)
    if not np.any(false_positive_result):
        return None

    vtk_result_img = numpy_to_vtk_img(false_positive_result, gt_vtk_img)
    return vtk_result_img

def false_negative(gt_vtk_img, pred_vtk_img):
    gt_np_img = vtk_img_to_numpy(gt_vtk_img)
    pred_np_img = vtk_img_to_numpy(pred_vtk_img)
    
    false_positive_result = np.logical_and(gt_np_img, np.logical_not(pred_np_img)).astype(np.uint8)
    if not np.any(false_positive_result):
        return None
    
    vtk_result_img = numpy_to_vtk_img(false_positive_result, gt_vtk_img)
    return vtk_result_img