import '../src/index.css'
import { MaintenanceLogProvider } from '../src/context/MaintenanceLogContext'
import { Toaster } from 'react-hot-toast'

function MyApp({ Component, pageProps }) {
  return (
    <MaintenanceLogProvider>
      <Component {...pageProps} />
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </MaintenanceLogProvider>
  )
}

export default MyApp 