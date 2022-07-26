"""Unit test package for HoVerNet+."""

import copy

# ! The garbage collector
import gc
import multiprocessing
import pathlib
import shutil

import joblib
import numpy as np
import pytest

from tiatoolbox.models import MultiTaskSegmentor, SemanticSegmentor
from tiatoolbox.utils import env_detection as toolbox_env

ON_GPU = toolbox_env.has_gpu()
# The batch size value here is based on two TitanXP, each with 12GB
BATCH_SIZE = 1 if not ON_GPU else 16
try:
    NUM_POSTPROC_WORKERS = multiprocessing.cpu_count()
except NotImplementedError:
    NUM_POSTPROC_WORKERS = 2

# ----------------------------------------------------


def _rm_dir(path):
    """Helper func to remove directory."""
    shutil.rmtree(path, ignore_errors=True)


@pytest.mark.skipif(
    toolbox_env.running_on_ci() or not toolbox_env.has_gpu(),
    reason="Local test on machine with GPU.",
)
def test_functionality_local(remote_sample, tmp_path):
    """Local functionality test for multi task segmentor."""
    gc.collect()
    root_save_dir = pathlib.Path(tmp_path)
    mini_wsi_svs = pathlib.Path(remote_sample("svs-1-small"))

    save_dir = f"{root_save_dir}/multitask/"
    _rm_dir(save_dir)
    multi_segmentor = MultiTaskSegmentor(
        pretrained_model="hovernetplus-oed",
        batch_size=BATCH_SIZE,
        num_postproc_workers=NUM_POSTPROC_WORKERS,
    )
    output = multi_segmentor.predict(
        [mini_wsi_svs],
        mode="wsi",
        on_gpu=ON_GPU,
        crash_on_exception=True,
        save_dir=save_dir,
    )

    inst_dict = joblib.load(f"{output[0][1]}.0.dat")
    layer_map = np.load(f"{output[0][1]}.1.npy")

    assert len(inst_dict) > 0, "Must have some nuclei"
    assert layer_map is not None, "Must have some layers."
    _rm_dir(tmp_path)


def test_functionality_hovernetplus_travis(remote_sample, tmp_path):
    """Functionality test for multi task segmentor."""
    root_save_dir = pathlib.Path(tmp_path)
    mini_wsi_svs = pathlib.Path(remote_sample("wsi4_512_512_svs"))
    required_dims = (258, 258)
    # above image is 512 x 512 at 0.252 mpp resolution. This is 258 x 258 at 0.500 mpp.

    save_dir = f"{root_save_dir}/multi/"
    _rm_dir(save_dir)

    multi_segmentor = MultiTaskSegmentor(
        pretrained_model="hovernetplus-oed",
        batch_size=BATCH_SIZE,
        num_postproc_workers=NUM_POSTPROC_WORKERS,
    )
    output = multi_segmentor.predict(
        [mini_wsi_svs],
        mode="wsi",
        on_gpu=ON_GPU,
        crash_on_exception=True,
        save_dir=save_dir,
    )

    inst_dict = joblib.load(f"{output[0][1]}.0.dat")
    layer_map = np.load(f"{output[0][1]}.1.npy")

    assert len(inst_dict) > 0, "Must have some nuclei."
    assert layer_map is not None, "Must have some layers."
    assert (
        layer_map.shape == required_dims
    ), "Output layer map dimensions must be same as the expected output shape"
    _rm_dir(tmp_path)


def test_functionality_hovernet_travis(remote_sample, tmp_path):
    """Functionality test for multi task segmentor."""
    root_save_dir = pathlib.Path(tmp_path)
    mini_wsi_svs = pathlib.Path(remote_sample("wsi4_512_512_svs"))

    save_dir = f"{root_save_dir}/multi/"
    _rm_dir(save_dir)

    multi_segmentor = MultiTaskSegmentor(
        pretrained_model="hovernet_fast-pannuke",
        batch_size=BATCH_SIZE,
        num_postproc_workers=NUM_POSTPROC_WORKERS,
    )
    output = multi_segmentor.predict(
        [mini_wsi_svs],
        mode="wsi",
        on_gpu=ON_GPU,
        crash_on_exception=True,
        save_dir=save_dir,
    )

    inst_dict = joblib.load(f"{output[0][1]}.0.dat")

    assert len(inst_dict) > 0, "Must have some nuclei."
    _rm_dir(tmp_path)


def test_functionality_process_instance_predictions(remote_sample, tmp_path):
    root_save_dir = pathlib.Path(tmp_path)
    mini_wsi_svs = pathlib.Path(remote_sample("wsi4_512_512_svs"))

    save_dir = f"{root_save_dir}/semantic/"
    _rm_dir(save_dir)

    semantic_segmentor = SemanticSegmentor(
        pretrained_model="hovernetplus-oed",
        batch_size=BATCH_SIZE,
        num_postproc_workers=2,
    )
    multi_segmentor = MultiTaskSegmentor(
        pretrained_model="hovernetplus-oed",
        batch_size=BATCH_SIZE,
        num_postproc_workers=2,
    )

    output = semantic_segmentor.predict(
        [mini_wsi_svs],
        mode="wsi",
        on_gpu=True,
        crash_on_exception=True,
        save_dir=save_dir,
    )
    raw_maps = [np.load(f"{output[0][1]}.raw.{head_idx}.npy") for head_idx in range(4)]
    _, inst_dict_b, layer_map, _ = semantic_segmentor.model.postproc(raw_maps)

    dummy_reference = [{i: {"box": np.array([0, 0, 32, 32])} for i in range(1000)}]

    dummy_tiles = [np.zeros((512, 512))]
    dummy_bounds = np.array([0, 0, 512, 512])

    multi_segmentor.wsi_layers = [np.zeros_like(raw_maps[0][..., 0])]
    multi_segmentor._wsi_inst_info = copy.deepcopy(dummy_reference)
    multi_segmentor._futures = [
        [dummy_reference, [dummy_reference[0].keys()], dummy_tiles, dummy_bounds]
    ]
    multi_segmentor._merge_post_process_results()
    assert len(multi_segmentor._wsi_inst_info[0]) == 0
