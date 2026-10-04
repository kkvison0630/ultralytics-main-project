# 加载所需的R包
install.packages("pheatmap")
library(pheatmap) 
# 用于绘制热图
library(RColorBrewer)# 颜色包
library(extrafont)
font_import()
#读取作图数据
data = read.csv("E:/Fig6b-heart-z.csv", header = TRUE, row.names = 1,sep = ",")
# 从文件读取CSV数据，"文件名.csv"：
# header = TRUE：表示CSV文件的第一行是列名,row.names = 1:第一列为行名。

# 生成热图
heatmap_result = pheatmap(data,         
                          breaks = seq(-3.5, 3.5, length.out = 101),# 颜色范围和断点
                           col = colorRampPalette(c(
                            "#E6F3FF",  "#A8D8EA", "#8DCCE3", 
                            "#7ACCCE", "#78D6B9", "#8AE0B9",
                            "#FFFAE6","#FFD6B8",  "#FF9A76" ))(100),  #基因表达的渐变色设置
                            legend_breaks = c(-3.5, -1.7, 0, 1.7, 3.5),  # 显示哪些刻度
         # 热图的颜色，可调整为Blues、Reds、YlOrRd等 
         cluster_rows = FALSE,# 是否对行（指标）进行聚类
         cluster_cols = TRUE,# 是否对列（物质）进行聚类
         clustering_distance_rows = "euclidean",  
         # 聚类距离（行）指定用于行的聚类距离度量方法，这里使用欧几里得距离。         
         clustering_distance_cols = "euclidean",  # 聚类距离（列）         
         clustering_method = "complete",# 聚类方法         
         display_numbers = FALSE, # 是否显示数字
         fontfamily = "Times New Roman", # 是否显示相关系数值
         treeheight_col = 40) # 树枝高度


# 初始化一个列表来存储结果
distance_list <- list()

# 计算每两列之间的每一行元素的欧氏距离
for (i in 1:(ncol(data)-1)) {
  for (j in (i+1):ncol(data)) {
    # 计算第i列和第j列之间每一行元素的欧氏距离
    distances <- sqrt((data[, i] - data[, j])^2)
    # 存储结果
    distance_list[[paste0("Col", i, "_Col", j)]] <- distances
  }
}

# 打印结果
for (name in names(distance_list)) {
  cat(name, ":\n")
  print(distance_list[[name]])
  cat("\n")
}