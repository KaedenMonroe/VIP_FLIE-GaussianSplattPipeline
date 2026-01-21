import os
import shutil
import cv2
import numpy as np
import multiprocessing
from glob import glob
import argparse

class BlurFilter:
    def __init__(self, source_dir, output_dir, target_count=None, target_percentage=0.95, groups=None, scalar=None, dry_run=False):
        """
        Initialize the BlurFilter.
        
        Args:
            source_dir (str): Path to the directory containing image frames.
            output_dir (str): Path to the directory to save the filtered images.
            target_count (int): Explicit number of images to keep.
            target_percentage (float): Percentage of images to keep (0.0 to 1.0).
            groups (int): Number of groups to split the timeline into.
            dry_run (bool): If True, simulate actions.
        """

        self.source_dir = source_dir
        self.output_dir = output_dir
        self.target_count = target_count
        self.target_percentage = target_percentage
        self.groups = groups
        self.scalar = scalar
        self.dry_run = dry_run
        
        if self.output_dir and not os.path.exists(self.output_dir):
            if not self.dry_run:
                os.makedirs(self.output_dir)

    def _variance_of_laplacian(self, image):
        """Compute the Laplacian variance as a sharpness metric."""
        return cv2.Laplacian(image, cv2.CV_64F).var()

    def _distribute_evenly(self, total: int, num_groups: int) -> list[int]:
        """
        Helper to distribute images/slots evenly across groups.
        Deals with floating point errors by incrementing the first few groups.
        """
        ideal_per_group = total / num_groups
        if ideal_per_group < 1:
            raise ValueError("Number of groups must be less than the total number of images.")
        accumulated_error = 0.0
        distribution = [0] * num_groups

        for i in range(num_groups):
            distribution[i] = int(ideal_per_group)
            accumulated_error += ideal_per_group - distribution[i]

            while accumulated_error >= 1.0:
                distribution[i] += 1
                accumulated_error -= 1.0

        return distribution

    def _find_image_directories(self):
        """
        Scans source_dir for directories containing images.
        Returns a list of (input_dir, output_dir) tuples.
        """
        image_dirs = []
        extensions = {'.jpg', '.jpeg', '.png'}
        
        # Check if source_dir itself has images (Single Mode)
        has_images = False
        for fname in os.listdir(self.source_dir):
            if os.path.splitext(fname)[1].lower() in extensions:
                has_images = True
                break
        
        if has_images:
            image_dirs.append((self.source_dir, self.output_dir))
        
        # Check subdirectories (Batch Mode)
        # We walk top-down. If we find a directory with images, we add it.
        # Note: This simple logic assumes either root has images OR subdirs have images, 
        # but robust code handles mixed.
        for root, dirs, files in os.walk(self.source_dir):
            if root == self.source_dir and has_images:
                continue # Already added
                
            # Check if this dir has images
            dir_has_images = any(os.path.splitext(f)[1].lower() in extensions for f in files)
            
            if dir_has_images:
                # Construct relative path
                rel_path = os.path.relpath(root, self.source_dir)
                out_path = os.path.join(self.output_dir, rel_path)
                image_dirs.append((root, out_path))
                
        return image_dirs

    def run(self):
        print(f"--- Starting Blur Filter on {self.source_dir} ---")
        
        target_dirs = self._find_image_directories()
        
        if not target_dirs:
            print("No directories with images found.")
            return

        print(f"Found {len(target_dirs)} directories to process.")

        total_copied = 0
        
        for in_dir, out_dir in target_dirs:
            print(f"Processing: {in_dir}")
            
            if out_dir and not os.path.exists(out_dir) and not self.dry_run:
                os.makedirs(out_dir, exist_ok=True)
                
            copied = self._process_directory(in_dir, out_dir)
            total_copied += copied

        print("-" * 30)
        print(f"Blur Filter Complete. Total images copied: {total_copied}")
        
    def _process_directory(self, source_dir, output_dir):
        # 1. Gather Images
        extensions = ['*.jpg', '*.jpeg', '*.png']
        images = []
        for ext in extensions:
            images.extend(glob(os.path.join(source_dir, ext)))
            images.extend(glob(os.path.join(source_dir, ext.upper())))
        
        unique_images_dict = {os.path.normcase(path): path for path in images}
        final_images = sorted(unique_images_dict.values())
        total_images = len(final_images)
        
        if total_images == 0:
            return 0

        # ... (Logic from original run) ...
        # 2. Determine Targets
        # Recalculate per directory or use global targets?
        # Typically per-video targets (e.g. keep 95% of THIS video)
        
        current_target_count = self.target_count
        if current_target_count is None:
             current_target_count = int(total_images * self.target_percentage)
             
        # Groups
        current_groups = self.groups
        if current_groups is None:
            current_groups = current_target_count
            
        if current_groups <= 0: # Safety
            current_groups = 1

        print(f"  {total_images} images. Keeping {current_target_count} (Groups: {current_groups}).")

        # 4. Calculate Sharpness Scores
        image_scores = []
        # print("  Calculating scores...") 
        for img_path in final_images:
            img = cv2.imread(img_path)
            if img is None: continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            score = self._variance_of_laplacian(gray)
            image_scores.append((score, img_path))
        
        # 5. Group and Select
        if current_groups > total_images:
             # Fallback if groups > images (e.g. very short video)
             current_groups = total_images
             
        group_sizes = self._distribute_evenly(total_images, current_groups)
        keep_per_group = self._distribute_evenly(current_target_count, current_groups)
        
        selected_images = set()
        offset = 0
        
        for idx, size in enumerate(group_sizes):
            end_idx = offset + size
            chunk = image_scores[offset:end_idx]
            chunk_sorted = sorted(chunk, key=lambda x: x[0], reverse=True)
            
            n_to_keep = keep_per_group[idx]
            kept_chunk = chunk_sorted[:n_to_keep]
            
            for _, path in kept_chunk:
                selected_images.add(path)
            offset = end_idx

        # 6. Output Selection
        if not output_dir:
            return 0

        copied_count = 0
        for path in selected_images:
            filename = os.path.basename(path)
            dest = os.path.join(output_dir, filename)
            copied_count += 1
            
            if self.dry_run:
                # print(f"[PREDICTION] Would copy: {filename}")
                pass
            else:
                try:
                    shutil.copy2(path, dest)
                except Exception as e:
                    print(f"Error copying {filename}: {e}")
                    
        return copied_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blur Filter Script")
    parser.add_argument("--input_dir", required=True, help="Path to input directory")
    parser.add_argument("--output_dir", required=True, help="Path to output directory")
    parser.add_argument("--target_count", type=int, default=None, help="Specific number of images to keep")
    parser.add_argument("--keep_percent", type=float, default=0.95, help="Percentage to keep (0.0-1.0)")
    parser.add_argument("--groups", type=int, default=None, help="Number of groups")
    parser.add_argument("--scalar", type=int, default=1, help="Scalar value")
    parser.add_argument("--dry_run", action="store_true", help="Run without copying files")

    args = parser.parse_args()

    # Handle 'None' passed strings from some CLI builders if necessary, but argparse handles types well.
    # Just initiate directly
    blur_filter = BlurFilter(
        source_dir=args.input_dir,
        output_dir=args.output_dir,
        target_count=args.target_count,
        target_percentage=args.keep_percent,
        groups=args.groups,
        scalar=args.scalar,
        dry_run=args.dry_run
    )
    blur_filter.run()
