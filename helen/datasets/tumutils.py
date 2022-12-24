from typing import Optional
import sys

import numpy as np
import warnings

__all__ = ["read_trajectory", "read_file_list", "associate"]


_EPS = np.finfo(float).eps * 4.0


def transform44(l: tuple):
    r"""Generate a 4x4 homogeneous transformation matrix from a 3D point and unit quaternion.

    Args:
        l (tuple): tuple consisting of (stamp,tx,ty,tz,qx,qy,qz,qw) where (tx,ty,tz) is the
            3D position and (qx,qy,qz,qw) is the unit quaternion.

    Returns:
        np.ndarray: 4x4 homogeneous transformation matrix

    Shape:
        - Output: `(4, 4)`
    """
    t = l[1:4]
    q = np.array(l[4:8], dtype=np.float64, copy=True)
    nq = np.dot(q, q)
    if nq < _EPS:
        return np.array(
            (
                (1.0, 0.0, 0.0, t[0]),
                (0.0, 1.0, 0.0, t[1]),
                (0.0, 0.0, 1.0, t[2]),
                (0.0, 0.0, 0.0, 1.0),
            ),
            dtype=np.float64,
        )
    q *= np.sqrt(2.0 / nq)
    q = np.outer(q, q)
    return np.array(
        (
            (1.0 - q[1, 1] - q[2, 2], q[0, 1] - q[2, 3], q[0, 2] + q[1, 3], t[0]),
            (q[0, 1] + q[2, 3], 1.0 - q[0, 0] - q[2, 2], q[1, 2] - q[0, 3], t[1]),
            (q[0, 2] - q[1, 3], q[1, 2] + q[0, 3], 1.0 - q[0, 0] - q[1, 1], t[2]),
            (0.0, 0.0, 0.0, 1.0),
        ),
        dtype=np.float64,
    )


def read_trajectory(filename: str, matrix: bool = True):
    r"""Read a trajectory from a text file.

    Args:
        filename: Path of file to be read
        matrix (np.ndarray or tuple): If True, will convert poses to 4x4 homogeneous transformation
            matrices (of type np.ndarray). Else, will return poses as tuples consisting of
            (stamp,tx,ty,tz,qx,qy,qz,qw), where (tx,ty,tz) is the 3D position and (qx,qy,qz,qw)
            is the unit quaternion.

    Returns:
        dict: dictionary of {stamp: pose} where stamp is of type str and pose is a 4x4 np.ndarray if matrix is True,
            or a tuple of position and unit quaternion (tx,ty,tz,qx,qy,qz,qw) if matrix is False.

    """
    file = open(filename)
    data = file.read()
    lines = data.replace(",", " ").replace("\t", " ").split("\n")
    list = []
    for line in lines:
        line_list = []
        if len(line) > 0 and line[0] != "#":
            for n, v in enumerate(line.split(" ")):
                v = v.strip()
                if v != "":
                    v = float(v) if n > 0 else v
                    line_list.append(v)
            list.append(line_list)
    list_ok = []
    for i, l in enumerate(list):
        if l[4:8] == [0, 0, 0, 0]:
            continue
        isnan = False
        for v in l[1:]:
            if np.isnan(v):
                isnan = True
                break
        if isnan:
            sys.stderr.write(
                "Warning: line %d of file '%s' has NaNs, skipping line\n"
                % (i, filename)
            )
            continue
        list_ok.append(l)
    if matrix:
        traj = dict([(l[0], transform44(l[0:])) for l in list_ok])
    else:
        traj = dict([(l[0], l[1:8]) for l in list_ok])
    return traj


def read_file_list(
    filename: str, start: Optional[int] = None, end: Optional[int] = None
):
    r"""Reads a sequence from a text file and returns a {stamp: [d1, d2, d3, ...]} dictionary. The file should
    be a .txt file where each line contains "stamp d1 d2 d3 ...", where "stamp" and "d1 d2 d3 ..." denote
    the time stamp and data respectively.

    Args:
        filename (str): Path to text file, where text file has the format: "stamp d1 d2 d3 ..."
        start (int or None): Index of frame to start stamp/data extraction from.
            If None, will start from the first frame. Default: None
        end (int or None): Index of frame to end stamp/data extraction at.
            If None, will end at the final frame. Default: None

    Returns:
        dict: dictionary of {stamp: [d1, d2, d3]} keys and values, where stamp is of type str

    """
    file = open(filename)
    data = file.read()
    lines = data.replace(",", " ").replace("\t", " ").split("\n")
    list = [
        [v.strip() for v in line.split(" ") if v.strip() != ""]
        for num, line in enumerate(lines)
        if len(line) > 0 and line[0] != "#"
    ]
    start = start if start is not None else 0
    end = end if end is not None else len(lines)
    if end > len(lines):
        msg = '"end" was larger than number of frames in "{0}": {1} > {2}'
        warnings.warn(msg.format(filename, end, len(lines)))
    list = list[start:end]
    list = [(l[0], l[1:]) for l in list if len(l) > 1]
    return dict(list)


def associate(
    first_dict: dict, second_dict: dict, offset: float, max_difference: float
):
    r"""Associate two dictionaries of {stamp1: data1} and {stamp2: data2} by returning
    (stamp1, stamp2). As the time stamps never match exactly, we aim to find the
    closest stamp match between input dictionaries.

    Args:
        first_dict (dict): First dictionary of {stamp1: data1} where stamp1 is of type str
        second_dict (dict): Second dictionary of {stamp2: data2} where stamp2 is of type str
        offset (float): Time offset between both dictionaries (e.g., to model the delay between the sensors)
        max_difference (float): Search radius for candidate generation

    Returns:
        matches (list of tuple of str): List of matched tuples (stamp1, stamp2)

    """
    first_keys = list(first_dict.keys())
    second_keys = list(second_dict.keys())
    potential_matches = [
        (abs(float(a) - (float(b) + offset)), a, b)
        for a in first_keys
        for b in second_keys
        if abs(float(a) - (float(b) + offset)) < max_difference
    ]
    potential_matches.sort()
    matches = []
    for diff, a, b in potential_matches:
        if a in first_keys and b in second_keys:
            first_keys.remove(a)
            second_keys.remove(b)
            matches.append((a, b))

    matches.sort()
    return matches
