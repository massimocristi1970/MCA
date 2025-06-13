import joblib

# Path to your scaler file
scaler_path = r"C:\Users\Massimo Cristi\OneDrive\Documents\GitHub\MCA\scaler.pkl"

# Load the scaler
scaler = joblib.load(scaler_path)

# Print out the mean and scale (standard deviation) of each feature
print("Feature Means:")
print(scaler.mean_)

print("\nFeature Standard Deviations:")
print(scaler.scale_)