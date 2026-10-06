
import os
import matplotlib.pyplot as plt
from IPython.display import Image, display

os.makedirs("visualizations", exist_ok=True)

=====================================================
# 1. Return rate by payment method
=====================================================

rate = df_merged.groupby('payment_method')['returned'].mean().mul(100).sort_values(ascending=False)

plt.figure(figsize=(7, 5))
bars = plt.bar(rate.index, rate.values)

for bar, value in zip(bars, rate.values):
    plt.text(bar.get_x() + bar.get_width()/2, value + 1,
             f'{value:.1f}%', ha='center')

plt.ylabel('Return Rate (%)')
plt.xlabel('Payment Method')
plt.title('COD Returns at 44.4% — 3x Card')
plt.tight_layout()
image_path = 'visualizations/return_rate_by_payment.png'
plt.savefig(image_path)
plt.close()

# Display the saved PNG
display(Image(filename=image_path))
print("Visualizations saved and displayed successfully.")

==================================================================
# 2. Outlier-corrected monthly revenue
==================================================================

df_merged['order_date'] = pd.to_datetime(df_merged['order_date'])
df_merged['month'] = df_merged['order_date'].dt.to_period('M')

outliers = ['O0011', 'O0098']
corrected = df_merged[~df_merged['order_id'].isin(outliers)]

monthly = corrected.groupby('month')['order_value'].sum()
peak = monthly.idxmax()

plt.figure(figsize=(8, 5))
plt.plot(monthly.index.astype(str), monthly.values, marker='o')

plt.xlabel('Month')
plt.ylabel('Revenue')
plt.title(f'Monthly Revenue Trend — Peak: {peak}')
plt.xticks(rotation=45)
plt.tight_layout()

path2 = 'visualizations/monthly_revenue_trend.png'
plt.savefig(path2)
plt.show()

display(Image(filename=path2))

print("Both PNGs saved in the visualizations/ folder.")
