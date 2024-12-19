import os
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Define the directory to search for .txt files
results_dir = 'results'
images_dir = 'graphs'

# Create the images directory if it doesn't exist
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Get all .txt files in the results directory
txt_files = [f for f in os.listdir(results_dir) if f.endswith('.txt')]

# Open a file to save the statistical information
with open('statistical_analysis_results.txt', 'w') as result_file:
    for filename in txt_files:
        # Extract date from the filename
        date_str = filename.split('_')[0]

        # Step 1: Read the text file and extract transfer times, image name, and NINA Power mode configuration
        transfer_times = []
        image_name = None
        nina_power_mode = None
        with open(os.path.join(results_dir, filename), 'r') as file:
            for line in file:
                if not image_name:
                    image_match = re.search(r'Download image (.+)', line)
                    if image_match:
                        image_name = image_match.group(1)
                if not nina_power_mode:
                    nina_match = re.search(r'NINA Power mode configuration: (.+)', line)
                    if nina_match:
                        nina_power_mode = nina_match.group(1)
                match = re.search(r'Transfer time: (\d+\.\d+) milliseconds', line)
                if match:
                    transfer_times.append(float(match.group(1)))

        # Step 2: Calculate statistical measures
        mean_transfer_time = np.mean(transfer_times)
        median_transfer_time = np.median(transfer_times)
        std_dev_transfer_time = np.std(transfer_times)
        variance_transfer_time = np.var(transfer_times)

        # Write the statistical information to the result file
        result_file.write(f"Processing file: {filename}\n")
        result_file.write(f"Image file: {image_name}\n")
        result_file.write(f"NINA Power mode configuration: {nina_power_mode}\n")
        result_file.write(f"Mean: {mean_transfer_time:.2f} ms\n")
        result_file.write(f"Median: {median_transfer_time:.2f} ms\n")
        result_file.write(f"Standard Deviation: {std_dev_transfer_time:.2f} ms\n")
        result_file.write(f"Variance: {variance_transfer_time:.2f} ms\n\n")

        # Step 3: Plot the normal distribution
        plt.figure(figsize=(10, 6))
        plt.hist(transfer_times, bins=30, density=True, alpha=0.6, color='g', label='Transfer Time Histogram')

        # Plot the normal distribution curve
        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mean_transfer_time, std_dev_transfer_time)
        plt.plot(x, p, 'k', linewidth=2, label='Normal Distribution')

        title = f"Results for {image_name}:\nmean = {mean_transfer_time:.2f} ms std dev = {std_dev_transfer_time:.2f} ms\nNINA Power mode: {nina_power_mode}"
        plt.title(title, fontdict={'fontsize': 14, 'fontweight': 'bold'})

        plt.xlabel('Transfer Time (ms)')
        plt.ylabel('Density')

        # Add legend
        plt.legend()

        # Save the plot as an image file with date and image name
        output_filename = os.path.join(images_dir, f'{date_str}_{image_name}_results.png')
        plt.savefig(output_filename)
        plt.close()