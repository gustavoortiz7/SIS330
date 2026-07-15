import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:video_player/video_player.dart';
import 'package:path_provider/path_provider.dart';
import 'package:http_parser/http_parser.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  runApp(MyApp(cameras: cameras));
}

class MyApp extends StatelessWidget {
  final List<CameraDescription> cameras;
  const MyApp({super.key, required this.cameras});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Voley Project',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: HomeScreen(cameras: cameras),
    );
  }
}

class HomeScreen extends StatelessWidget {
  final List<CameraDescription> cameras;
  const HomeScreen({super.key, required this.cameras});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voley Project'),
        backgroundColor: Color(0xFF0033A0), // Azul Marino
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: <Widget>[
            DrawerHeader(
              decoration: BoxDecoration(
                color: Color(0xFF0033A0), // Azul Marino
              ),
              child: Text(
                'Menú',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                ),
              ),
            ),
            ListTile(
              leading: Icon(Icons.videocam),
              title: Text('Grabar Video'),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => RecordVideoScreen(cameras: cameras)),
                );
              },
            ),
            ListTile(
              leading: Icon(Icons.upload_file),
              title: Text('Subir Video'),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => VideoUploadScreen()),
                );
              },
            ),
          ],
        ),
      ),
      body: Container(
        color: Color(0xFFFFFFFF), // Fondo Blanco
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => RecordVideoScreen(cameras: cameras)),
                  );
                },
                child: Text('Grabar Video'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFF0033A0), // Azul Marino
                  padding: EdgeInsets.symmetric(horizontal: 50, vertical: 20),
                  textStyle: TextStyle(
                    color: Colors.white,
                    fontSize: 25,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => VideoUploadScreen()),
                  );
                },
                child: Text('Subir Video'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFFFFCC00), // Amarillo
                  padding: EdgeInsets.symmetric(horizontal: 50, vertical: 20),
                  textStyle: TextStyle(
                    color: Color(0xFF333333), // Gris Oscuro
                    fontSize: 25,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class RecordVideoScreen extends StatefulWidget {
  final List<CameraDescription> cameras;
  const RecordVideoScreen({super.key, required this.cameras});

  @override
  _RecordVideoScreenState createState() => _RecordVideoScreenState();
}

class _RecordVideoScreenState extends State<RecordVideoScreen> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  bool _isRecording = false;
  XFile? _videoFile;
  bool _isSending = false;
  VideoPlayerController? _videoPlayerController;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(widget.cameras[0], ResolutionPreset.max);
    _initializeControllerFuture = _controller.initialize();
  }

  Future<void> _startVideoRecording() async {
    if (!_isRecording) {
      try {
        await _controller.startVideoRecording();
        setState(() {
          _isRecording = true;
        });
      } catch (e) {
        print(e);
      }
    }
  }

  Future<void> _stopVideoRecording() async {
    if (_isRecording) {
      try {
        _videoFile = await _controller.stopVideoRecording();
        setState(() {
          _isRecording = false;
        });

        // Guardar el video cuando se detiene la grabación
        _saveVideo();
      } catch (e) {
        print(e);
      }
    }
  }

  // Método para guardar el video en el directorio de documentos
  Future<void> _saveVideo() async {
    if (_videoFile != null) {
      final Directory? directory = await getDownloadsDirectory();
      if (directory != null) {
        final String timestamp = DateTime.now().millisecondsSinceEpoch.toString();
        final String videoPath = '${directory.path}/video_$timestamp.mp4';

        final File videoFile = File(_videoFile!.path);
        await videoFile.copy(videoPath);

        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Video guardado en: $videoPath')));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('No se encontró el directorio de descargas')));
      }
    }
  }

  Future<void> _sendVideo() async {
    setState(() {
      _isSending = true;
    });

    if (_videoFile != null) {
      try {
        final videoBytes = await _videoFile!.readAsBytes();
        final uri = Uri.parse('http://192.168.238.137:8000/video');
        var request = http.MultipartRequest('POST', uri)
          ..files.add(http.MultipartFile.fromBytes(
            'video',
            videoBytes,
            filename: 'video.mp4',
            contentType: MediaType('video', 'mp4'),
          ));
        final response = await request.send();
        if (response.statusCode == 200) {
          final processedVideoBytes = await response.stream.toBytes();
          final Directory? directory = await getDownloadsDirectory();
          if (directory != null) {
            final String timestamp = DateTime.now().millisecondsSinceEpoch.toString();
            final processedVideoPath = '${directory.path}/processed_$timestamp.mp4';
            final processedVideoFile = File(processedVideoPath);
            await processedVideoFile.writeAsBytes(processedVideoBytes);
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Video procesado guardado en: $processedVideoPath')));

            // Reproducir video guardado
            _videoPlayerController = VideoPlayerController.file(processedVideoFile)
              ..initialize().then((_) {
                setState(() {});
                _videoPlayerController?.play();
              });
          } else {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('No se encontró el directorio de descargas')));
          }
        } else {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${response.statusCode}')));
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      } finally {
        setState(() {
          _isSending = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _videoPlayerController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Grabar Video'),
        backgroundColor: Color(0xFF0033A0), // Azul Marino
      ),
      body: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return Stack(
              children: [
                CameraPreview(_controller),
                if (_videoFile != null && !_isSending)
                  Positioned(
                    bottom: 16,
                    left: 16,
                    right: 16,
                    child: ElevatedButton(
                      onPressed: _sendVideo,
                      child: Text('Enviar Video'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Color(0xFFFFCC00), // Amarillo
                        padding: EdgeInsets.symmetric(horizontal: 50, vertical: 20),
                        textStyle: TextStyle(
                          color: Color(0xFF333333), // Gris Oscuro
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                if (_isSending)
                  const Center(child: CircularProgressIndicator()),
                if (_videoPlayerController != null && _videoPlayerController!.value.isInitialized)
                  Positioned.fill(
                    child: GestureDetector(
                      onTap: () {
                        if (_videoPlayerController!.value.isPlaying) {
                          _videoPlayerController?.pause();
                        } else {
                          _videoPlayerController?.play();
                        }
                      },
                      child: AspectRatio(
                        aspectRatio: _videoPlayerController!.value.aspectRatio,
                        child: VideoPlayer(_videoPlayerController!),
                      ),
                    ),
                  ),
              ],
            );
          } else {
            return const Center(child: CircularProgressIndicator());
          }
        },
      ),
      floatingActionButton: Container(
        margin: EdgeInsets.only(bottom: 110,right: 190),
        width: 90,
        height: 90,
        child: FloatingActionButton(
          onPressed: _isRecording ? _stopVideoRecording : _startVideoRecording,
          child: Icon(_isRecording ? Icons.stop : Icons.videocam),
          backgroundColor: Color(0xFF0033A0), // Azul Marino
        ),
      ),
    );
  }
}

class VideoUploadScreen extends StatefulWidget {
  @override
  _VideoUploadScreenState createState() => _VideoUploadScreenState();
}

class _VideoUploadScreenState extends State<VideoUploadScreen> {
  VideoPlayerController? _videoPlayerController;
  bool _isSending = false;

  Future<void> _pickAndSendVideo() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickVideo(source: ImageSource.gallery);

    if (pickedFile != null) {
      setState(() {
        _isSending = true;
      });

      final videoFile = File(pickedFile.path);

      try {
        final videoBytes = await videoFile.readAsBytes();
        final uri = Uri.parse('http://192.168.238.137:8000/video');
        var request = http.MultipartRequest('POST', uri)
          ..files.add(http.MultipartFile.fromBytes(
            'video',
            videoBytes,
            filename: 'gallery_video.mp4',
            contentType: MediaType('video', 'mp4'),
          ));
        final response = await request.send();

        if (response.statusCode == 200) {
          final processedVideoBytes = await response.stream.toBytes();
          final Directory? directory = await getDownloadsDirectory();
          if (directory != null) {
            final String timestamp = DateTime.now().millisecondsSinceEpoch.toString();
            final processedVideoPath = '${directory.path}/gallery_$timestamp.mp4';
            final processedVideoFile = File(processedVideoPath);
            await processedVideoFile.writeAsBytes(processedVideoBytes);

            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Video enviado y procesado guardado en')));

            _videoPlayerController = VideoPlayerController.file(processedVideoFile)
              ..initialize().then((_) {
                setState(() {});
                _videoPlayerController?.play();
              });
          } else {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('No se encontró el directorio de descargas')));
          }
        } else {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error al enviar video: ${response.statusCode}')));
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      } finally {
        setState(() {
          _isSending = false;
        });
      }
    }
  }

@override
Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(
      title: const Text('Subir Video'),
      backgroundColor: Color(0xFF0033A0), // Azul Marino
    ),
    body: Column(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: <Widget>[
        if (_videoPlayerController != null && _videoPlayerController!.value.isInitialized)
          Expanded(
            child: GestureDetector(
              onTap: () {
                if (_videoPlayerController!.value.isPlaying) {
                  _videoPlayerController?.pause();
                } else {
                  _videoPlayerController?.play();
                }
              },
              child: AspectRatio(
                aspectRatio: _videoPlayerController!.value.aspectRatio,
                child: VideoPlayer(_videoPlayerController!),
              ),
            ),
          ),
        // Botón movido a una posición diferente
        Stack(
          children: [
            Align(
              alignment: Alignment.center,
              child: ElevatedButton(
                onPressed: _pickAndSendVideo,
                child: Text('Seleccionar Video'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFFFFCC00), // Amarillo
                  padding: EdgeInsets.symmetric(horizontal: 50, vertical: 20),
                  textStyle: TextStyle(
                    color: Color(0xFF333333), // Gris Oscuro
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
        if (_isSending)
          const Center(child: CircularProgressIndicator()),
      ],
    ),
  );
}


  @override
  void dispose() {
    _videoPlayerController?.dispose();
    super.dispose();
  }
}

