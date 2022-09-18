import json
import datetime
from collections import defaultdict
from itertools import combinations

# from detection import Detection
from . import Detection
from itertools import product
from math import inf, sqrt
from typing import Optional, Tuple

import pandas as pd
import numpy as np

# Common types
FrameID = int
ObjectID = str
DateTime = datetime.datetime
Coordinate2D = Tuple[float, float]
Speed2D = Tuple[float, float]
DetectionID = str
DataFrame = pd.DataFrame

# Euclidian distance between 2 objects in 2D
dist = lambda x, y: sqrt((x[0] - y[0]) * (x[0] - y[0]) + (x[1] - y[1]) * (x[1] - y[1]))


class Session:
    def __init__(
        self,
        filename: Optional[str] = "metadata.json",
        filterRolls: Optional[bool] = True,
    ) -> None:
        # load metadata from JSON file
        with open(filename) as f:
            data = json.load(f)

        self.stat_table = pd.DataFrame(
            {
                "frame": [],
                "timestamp": [],
                "obj1_id": [],
                "obj2_id": [],
                "obj1_type": [],
                "obj2_type": [],
                "x1": [],
                "y1": [],
                "x2": [],
                "y2": [],
                "distance": [],
                "speed": [],
            }
        )
        self.data = []
        self.detections = {}

        self.detectionsobjects = {"forklift": set(), "person": set()}

        # dict with object ids that were seen for the specific frame
        self.framesobjects = defaultdict(set)

        # loop by lists in data
        for d in data:
            filtered_detections = []
            frame_id, ts = d["frame_id"], d["timestamp"]
            for o in d["detections"]:
                detection_class, object_id = o["class"], o["id"]
                if detection_class != "roll":
                    self.framesobjects[frame_id].add(object_id)
                    self.detectionsobjects[detection_class].add(object_id)

                    x, y = (
                        o["warehouse_coordinates"]["X"],
                        o["warehouse_coordinates"]["Y"],
                    )
                    filtered_detections.append(o)

                    if object_id not in self.detections:
                        self.detections[object_id] = Detection(
                            id=o["id"],
                            detection_class=o["class"],
                            frame=frame_id,
                            timestamp=ts,
                            x=x,
                            y=y,
                        )
                    else:
                        self.detections[object_id].add_frame(frame_id, ts, x, y)
            d["detections"] = filtered_detections
            self.stat_table = self.__add_stat_row(
                self.stat_table, self.detections, self.framesobjects[frame_id], frame_id
            )
            self.data.append(d)

    def __add_stat_row(
        self, df: DataFrame, detections: dict, framesobjects: dict, frame_id: FrameID
    ) -> DataFrame:
        # less than one object on the frame
        if len(framesobjects) < 2 or not detections:
            return df

        for id1, id2 in combinations(sorted(framesobjects), 2):
            d1 = detections[id1]
            d2 = detections[id2]
            x1, y1 = d1.get_coord(frame_id)
            x2, y2 = d2.get_coord(frame_id)
            ts = d1.get_timestamp(frame_id)
            distance = dist([x1, y1], [x2, y2])

            search_slice = (df["obj1_id"] == id1) & (df["obj2_id"] == id2)
            if any(search_slice):
                distance_before = float(df[search_slice].iloc[[-1]]["distance"])
                frame_before = FrameID(df[search_slice].iloc[[-1]]["frame"])
                ts_before = d1.get_timestamp(frame_before)
                dd = distance - distance_before
                dt = (ts - ts_before).total_seconds()
                speed = dd / dt
            else:
                speed = np.nan
            df_to_add = pd.DataFrame(
                {
                    "frame": [frame_id],
                    "timestamp": [ts],
                    "obj1_id": [id1],
                    "obj2_id": [id2],
                    "obj1_type": [d1.detection_class],
                    "obj2_type": [d2.detection_class],
                    "x1": [x1],
                    "y1": [y1],
                    "x2": [x2],
                    "y2": [y2],
                    "distance": [distance],
                    "speed": [speed],
                }
            )
            df = pd.concat([df, df_to_add])
        return df

    def detect_forklifts_and_people(
        self, frame_id: Optional[FrameID] = None
    ) -> Tuple[set[DetectionID], set[DetectionID]]:
        """Return two sets of forlifts IDs and people IDs

        Args:
            frame_id (Optional[int], optional): frame id in the metadata. Defaults to None.

        Returns:
            Tuple[set, set]: (forklift ids, people ids)
        """
        if frame_id is None:
            # choose the last frame if frame_id is not defined
            frame_id = max(self.framesobjects.keys())

        forklifts = self.detectionsobjects["forklift"] & self.framesobjects[frame_id]
        people = self.detectionsobjects["person"] & self.framesobjects[frame_id]
        return forklifts, people

    def get_distances(
        self, frame_id: Optional[FrameID] = None, dt: Optional[float] = 0
    ) -> defaultdict:
        d = defaultdict(lambda: inf)

        """ Get distances between forklifts and people. If dt >0 then return projected distances between forklifts and people in dt times

        Returns:
            [type]: dictionary with distances between forklifts and people, if dt > 0 then it returns projected distance
        """
        forklifts, people = self.detect_forklifts_and_people(frame_id)
        # if we have no people and forklift pairs we return empty object
        if not forklifts or not people:
            return d

        for fid, pid in product(people, forklifts):
            f, p = self.detections[fid], self.detections[pid]
            d[(fid, pid)] = dist(
                f.get_coord_projection(frame_id, dt=dt),
                p.get_coord_projection(frame_id, dt=dt),
            )
        return d

    @property
    def min_time(self) -> datetime.datetime:
        return self.data[0]["timestamp"]

    @property
    def max_time(self):
        return self.data[-1]["timestamp"]

    @property
    def num_frames(self):
        return len(self.data)


if __name__ == "__main__":
    s = Session()
    print(s.min_time)
    print(s.max_time)
    print(s.data[300])
    for x in range(301, 700):
        d = s.get_distances(x)
        if d:
            print(x, d)

    # print(s.detections['630f114f1d7e45808606a3ef82ced639'].timestamps)
