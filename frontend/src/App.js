import LineChart from "./LineChart";
import EventTable from "./EventsTable";
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { useRef, useState } from "react";
import { ClimbingBoxLoader } from "react-spinners";
import { AppBar, Box, Button, Collapse, CssBaseline, Input, makeStyles, ThemeProvider, Toolbar, Typography } from "@material-ui/core";
import TileContainer from "./TileContainer";
import Tile from "./Tile";
import axios from 'axios';

const useStyles = makeStyles({
  toolbar: {
    paddingLeft:'60px',
    backgroundColor: 'white',
  },
});

function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [open, setOpen] = useState(true);
  const [videoPath, setVideoPath] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [tableData, setTableData] = useState([]);
  const [lineData, setLineData] = useState([]);

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const handleDownload = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/report', { responseType: 'blob' });
      const fileContent = response.data;
      const fileName = 'answer.json';
  
      const url = URL.createObjectURL(fileContent);
  
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      link.click();
  
      URL.revokeObjectURL(url);
    } catch (error) {
      alert(error);
    }
  };

  const handleChange = (events) => {
    const newFile = events.target.files[0];

    if (newFile == null)
      return;

      
    if (newFile && newFile.name.endsWith('.mp4')){
      setIsLoading(true);
      const formData = new FormData();
      formData.append('video', newFile);
      axios.post("http://127.0.0.1:5000/upload", formData, {
        onUploadProgress: progressEvent => {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          setUploadProgress(progress);
        }
      }).then(async (res) => {
        try {
          setLineData(await (await axios.get("http://127.0.0.1:5000/chart-data", { timeout: 5000 })).data);
        } catch (error) {
          alert(error);
        }
        try {
          setTableData(await (await axios.get("http://127.0.0.1:5000/table", { timeout: 5000 })).data);
        } catch (error) {
          alert(error);
        }
        setVideoPath(res.data.path);
        setIsLoading(false);
        setOpen(false);
      }).catch(error => {
        alert('Произошла ошибка при загрузке видео:' + error);
        setIsLoading(false);
      })
    }
    else {
      alert("Данный формат файла не поддерживается!");
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }

  const classes = useStyles();

  return (
    <div className="App">
      <ThemeProvider>
        <CssBaseline />
        <AppBar position="relative" style={{ marginBottom: 20 }}>
          <Toolbar className={classes.toolbar} >
            <img src="logo.svg" height={55}/>
          </Toolbar>
        </AppBar>

        <Dialog
          open={open}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title" p={2}>
            {!isLoading && "Выберите видеофайл"}
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description" p={2} style={{ textAlign: 'center' }}>
              {!isLoading && <Input ref={fileInputRef} onChange={e => handleChange(e)} type="file" accept=".mp4" label="Выберите файл"/>}
              {isLoading && 
              <>
                <ClimbingBoxLoader color="#36d7b7" cssOverride={{}} size={12} speedMultiplier={1}/>
                <Typography variant="p" align="center" style={{ fontWeight:'bold'}}>{uploadProgress} %</Typography>
              </>}
            </DialogContentText>
          </DialogContent>
        </Dialog>
        <Box>
          <Collapse in={!open} timeout={500}>
            <TileContainer>
              <Tile>
                <video width="550" height="400" ref={videoRef} controls >
                  {videoPath && <source src={videoPath} type="video/mp4"/>} 
                </video>
              </Tile>
              <Tile>
                <Box style={{ width: '300px',height: '200px', display:'flex', justifyContent:'center', flexDirection:'column'}}>
                  <Typography variant="h5" align="center" style={{ margin: '10px',marginBottom: '10px'}}>Результат анализа</Typography>
                  <Button variant="outlined" onClick={handleDownload} style={{ margin: '10px'}}>Скачать .json</Button>
                </Box>
              </Tile>
              <Tile>
                <EventTable videoRef={videoRef} data={!open ? tableData : []}/>
              </Tile>
              <Tile>
                <LineChart data={!open ? lineData : []}/>
              </Tile>
            </TileContainer>
          </Collapse>
        </Box>
      </ThemeProvider>
    </div>
  );
}

export default App;
