# MediaLibTools
**自用**的媒体库管理与同步小工具集

标记为粗体的文件是我经常用到的

| 文件                             | 说明                                                         |
| -------------------------------- | ------------------------------------------------------------ |
| **MusicSynchronizerForPhone.py** | 同步音乐库，先规范化文件名并移除不匹配的lrc文件，再以 256kbps m4a 的格式同步到电脑上的一个文件夹，然后将这个文件夹的内容通过adb同步到手机上。转换过程中会在当前目录下生成 temporary.xxx 图像文件供qaac读取封面。（需求 [adb](https://developer.android.com/studio/releases/platform-tools) / [qaac](https://github.com/nu774/qaac) / [ffmpeg](https://github.com/FFmpeg/FFmpeg) / 本项目中的一些其他文件） |
| MusicSynchronizerForMp3.py       | 同步音乐库，先以 160kbps mp3 的格式同步到电脑上的一个文件夹，然后由操作者手动（或使用别的同步软件，如SyncToy）将这个文件夹同步到MP3上。（需求 ffmpeg） |
| NoMatchedLrcRemover.py           | 移除没有匹配的音频文件的lrc文件                              |
| BrokenMediaClassifier.py         | 分类损坏的图像文件 ~~（和视频文件，但是还有问题）~~，~~用在了帮同学恢复相机数据上~~ |
| FileNameNormalizer.py            | 规范化文件名（像移除不换行空格之类的，避免在用adb操作文件时出现的编码问题） |
| MusicLibStat.py                  | 依据音频文件的创建日期 对不同时间点的总曲目数或作曲人的曲目数进行统计，生成供[数据可视化程序](https://github.com/Jannchie/Historical-ranking-data-visualization-based-on-d3.js)读取的csv文件，这是[效果](https://www.bilibili.com/video/BV1sj411o7VR) |
| rename.py                        | 批量重命名，分为关键词和正则方式                             |
| custom_adb.py                    | 封装好的一些adb功能，供其他程序调用                          |
| encoding_transformer.py          | 批量转换lrc文件的编码为mbcs                                  |

因为是自用的，所以大概率不会符合你的需求，也会比较简陋。发出来仅作分享。

使用了 [TinyTag](https://github.com/devsnd/tinytag) 项目来读取音频的tag信息

#### 参考：

- [QAAC 音频编码器命令行参数教程](https://www.nazorip.site/archives/44/)
